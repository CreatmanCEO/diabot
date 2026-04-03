"""Data models for DiaBot."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MealItem:
    """A single recognized food item."""

    name: str
    weight_g: int
    note: str = ""


@dataclass
class NutritionItem:
    """A food item with full nutrition data."""

    name: str
    weight_g: int
    calories: float
    protein: float
    fat: float
    carbs: float
    fiber: float
    gi: str = "medium"
    source: str = ""


@dataclass
class NutritionTotals:
    """Aggregated nutrition totals for a meal."""

    calories: float
    protein: float
    fat: float
    carbs: float
    fiber: float
    net_carbs: float
    he: float
    gi_overall: str = "medium"


@dataclass
class RecognitionResult:
    """Result of food recognition (Step 1)."""

    items: list[MealItem]
    is_food: bool
    confidence: str

    @classmethod
    def from_dict(cls, data: dict) -> RecognitionResult:
        items = []
        for item in data.get("items", []):
            # Filter to only known MealItem fields — LLM may return extras
            items.append(MealItem(
                name=item.get("name", ""),
                weight_g=item.get("weight_g", item.get("volume_ml", 0)),
                note=item.get("note", ""),
            ))
        return cls(
            items=items,
            is_food=data.get("is_food", False),
            confidence=data.get("confidence", "low"),
        )


@dataclass
class CalculationResult:
    """Result of nutrition calculation (Step 2)."""

    items: list[NutritionItem]
    totals: NutritionTotals

    @classmethod
    def from_dict(cls, data: dict) -> CalculationResult:
        items = []
        for item in data.get("items", []):
            # Filter to known NutritionItem fields — LLM may return extras
            items.append(NutritionItem(
                name=item.get("name", ""),
                weight_g=item.get("weight_g", item.get("volume_ml", 0)),
                calories=item.get("calories", 0),
                protein=item.get("protein", 0),
                fat=item.get("fat", 0),
                carbs=item.get("carbs", 0),
                fiber=item.get("fiber", 0),
                gi=item.get("gi", "medium"),
                source=item.get("source", ""),
            ))
        totals_data = data.get("totals", {})
        totals = NutritionTotals(
            calories=totals_data.get("calories", 0),
            protein=totals_data.get("protein", 0),
            fat=totals_data.get("fat", 0),
            carbs=totals_data.get("carbs", 0),
            fiber=totals_data.get("fiber", 0),
            net_carbs=totals_data.get("net_carbs", 0),
            he=totals_data.get("he", 0),
            gi_overall=totals_data.get("gi_overall", "medium"),
        )
        return cls(items=items, totals=totals)


@dataclass
class User:
    """User profile from database."""

    user_id: int
    username: str | None = None
    timezone: str = "Europe/Moscow"
    he_grams: int = 12
    language: str = "ru"
    is_active: bool = True
    onboarding_completed: bool = False
    consent_given_at: str | None = None
    created_at: str | None = None
    gender: str | None = None
    height_cm: int | None = None
    weight_kg: float | None = None
    age: int | None = None
    target_calories: int | None = None
    target_protein: int | None = None
    target_fat: int | None = None
    target_carbs: int | None = None
