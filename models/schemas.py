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
        items = [MealItem(**item) for item in data.get("items", [])]
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
        items = [NutritionItem(**item) for item in data.get("items", [])]
        totals = NutritionTotals(**data.get("totals", {}))
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
