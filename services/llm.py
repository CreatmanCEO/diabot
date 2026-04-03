"""LLM service with multi-provider fallback via litellm Router."""

import base64
import json
import logging
from typing import Any

from litellm import Router

from models.schemas import RecognitionResult, CalculationResult

logger = logging.getLogger(__name__)


class LLMService:
    """Manages LLM calls with vision and text chains."""

    def __init__(
        self,
        gemini_api_key: str = "",
        openrouter_api_key: str = "",
        groq_api_key: str = "",
    ) -> None:
        self.gemini_api_key = gemini_api_key
        self.openrouter_api_key = openrouter_api_key
        self.groq_api_key = groq_api_key

        self.vision_router = self._build_vision_router()
        self.text_router = self._build_text_router()

    def _build_vision_router(self) -> Router | None:
        """Build router for vision tasks (food photo recognition)."""
        models = []
        if self.gemini_api_key:
            models.append({
                "model_name": "vision",
                "litellm_params": {
                    "model": "gemini/gemini-2.5-flash",
                    "api_key": self.gemini_api_key,
                },
            })
        if self.openrouter_api_key:
            models.append({
                "model_name": "vision",
                "litellm_params": {
                    "model": "openrouter/google/gemini-2.5-flash",
                    "api_key": self.openrouter_api_key,
                },
            })
        if not models:
            return None
        return Router(model_list=models, num_retries=2, allowed_fails=1, cooldown_time=30)

    def _build_text_router(self) -> Router:
        """Build router for text tasks (KBJU calculation, corrections)."""
        models = []
        if self.gemini_api_key:
            models.append({
                "model_name": "text",
                "litellm_params": {
                    "model": "gemini/gemini-2.5-flash",
                    "api_key": self.gemini_api_key,
                },
            })
        if self.openrouter_api_key:
            models.append({
                "model_name": "text",
                "litellm_params": {
                    "model": "openrouter/google/gemini-2.5-flash",
                    "api_key": self.openrouter_api_key,
                },
            })
        if self.groq_api_key:
            models.append({
                "model_name": "text",
                "litellm_params": {
                    "model": "groq/meta-llama/llama-4-scout-17b-16e-instruct",
                    "api_key": self.groq_api_key,
                },
            })
        if not models:
            raise ValueError("Text chain requires at least one LLM API key")
        return Router(model_list=models, num_retries=2, allowed_fails=1, cooldown_time=30)

    async def recognize_food(
        self,
        image_bytes: bytes,
        prompt: str,
        caption: str | None = None,
    ) -> RecognitionResult:
        """Recognize food from photo using vision chain.

        Args:
            image_bytes: JPEG image bytes.
            prompt: System prompt for recognition.
            caption: Optional user caption with the photo.
        """
        if not self.vision_router:
            raise ValueError("Vision chain requires at least GEMINI_API_KEY or OPENROUTER_API_KEY")
        b64 = base64.b64encode(image_bytes).decode()
        content = [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
            {"type": "text", "text": prompt},
        ]
        if caption:
            content.append({"type": "text", "text": f"User caption: {caption}"})

        messages = [{"role": "user", "content": content}]
        return await self._call_recognition(self.vision_router, "vision", messages)

    async def recognize_food_text(
        self,
        text: str,
        prompt: str,
    ) -> RecognitionResult:
        """Recognize food from text description using text chain."""
        messages = [
            {"role": "user", "content": f"{prompt}\n\nUser description: {text}"},
        ]
        return await self._call_recognition(self.text_router, "text", messages)

    async def correct_recognition(
        self,
        previous_items: list[dict],
        correction: str,
        prompt: str,
        image_bytes: bytes | None = None,
    ) -> RecognitionResult:
        """Apply user correction to previous recognition."""
        # Format prompt with previous items and correction
        formatted_prompt = (
            prompt
            .replace("{previous_items}", json.dumps(previous_items, ensure_ascii=False))
            .replace("{correction_text}", correction)
        )

        if image_bytes:
            if not self.vision_router:
                raise ValueError("Vision chain requires at least GEMINI_API_KEY or OPENROUTER_API_KEY")
            b64 = base64.b64encode(image_bytes).decode()
            content = [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                {"type": "text", "text": formatted_prompt},
            ]
            messages = [{"role": "user", "content": content}]
            return await self._call_recognition(self.vision_router, "vision", messages)
        else:
            messages = [{"role": "user", "content": formatted_prompt}]
            return await self._call_recognition(self.text_router, "text", messages)

    async def calculate_nutrition(
        self,
        items: list[dict],
        prompt: str,
    ) -> CalculationResult:
        """Calculate KBJU for recognized items using text chain."""
        items_text = json.dumps(items, ensure_ascii=False)
        messages = [
            {"role": "user", "content": f"{prompt}\n\nProducts to calculate:\n{items_text}"},
        ]
        response = await self._call_with_retry(self.text_router, "text", messages)
        data = self._parse_json(response)
        return CalculationResult.from_dict(data)

    async def _call_recognition(
        self, router: Router, model_name: str, messages: list
    ) -> RecognitionResult:
        """Call LLM for recognition and parse result."""
        response = await self._call_with_retry(router, model_name, messages)
        data = self._parse_json(response)
        result = RecognitionResult.from_dict(data)

        # If low confidence, try Google Search grounding
        if result.is_food and result.confidence == "low":
            logger.info("Low confidence recognition, attempting search grounding")
            search_result = await self._search_grounding(result, messages)
            if search_result:
                return search_result

        return result

    async def _call_with_retry(
        self, router: Router, model_name: str, messages: list
    ) -> str:
        """Call LLM with JSON retry on parse failure."""
        response = await router.acompletion(
            model=model_name,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        content = response.choices[0].message.content

        # Validate JSON
        try:
            json.loads(content)
            return content
        except json.JSONDecodeError:
            logger.warning("Invalid JSON from LLM, retrying once")
            response = await router.acompletion(
                model=model_name,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1,
            )
            return response.choices[0].message.content

    async def _search_grounding(
        self, result: RecognitionResult, original_messages: list
    ) -> RecognitionResult | None:
        """Attempt Google Search grounding for low-confidence results."""
        if not self.gemini_api_key:
            return None
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.gemini_api_key)

            item_names = ", ".join(item.name for item in result.items)
            search_response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"Find accurate nutritional information for these food items: {item_names}. Return the product names and typical portion weights.",
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    response_mime_type="application/json",
                    temperature=0.1,
                ),
            )
            data = json.loads(search_response.text)
            return RecognitionResult.from_dict(data)
        except Exception as e:
            logger.warning("Search grounding failed: %s", e)
            return None

    @staticmethod
    def _parse_json(content: str) -> dict:
        """Parse JSON from LLM response content."""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if "```json" in content:
                start = content.index("```json") + 7
                end = content.index("```", start)
                return json.loads(content[start:end].strip())
            elif "```" in content:
                start = content.index("```") + 3
                end = content.index("```", start)
                return json.loads(content[start:end].strip())
            raise
