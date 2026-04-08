from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, field_validator


ALLOWED_CATEGORIES = {"Travel", "Office Supplies", "Utilities", "Misc"}


class InvoiceObservation(BaseModel):
    """Typed observation emitted by the environment at each step."""

    vendor_name: str
    invoice_date: str
    amount: float
    description: str
    metadata: Dict[str, Any]

    @field_validator("vendor_name")
    @classmethod
    def vendor_name_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("vendor_name cannot be empty")
        return value

    @field_validator("invoice_date")
    @classmethod
    def invoice_date_must_be_yyyy_mm_dd(cls, value: str) -> str:
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("invoice_date must be in YYYY-MM-DD format") from exc
        return value

    @field_validator("amount")
    @classmethod
    def amount_must_be_non_negative(cls, value: float) -> float:
        if value < 0:
            raise ValueError("amount must be non-negative")
        return value


class InvoiceAction(BaseModel):
    """Typed action sent by the agent."""

    extracted_fields: Dict[str, str]
    category: Optional[str] = None
    anomaly_flag: Optional[bool] = None

    @field_validator("extracted_fields")
    @classmethod
    def extracted_fields_must_contain_required_keys(cls, value: Dict[str, str]) -> Dict[str, str]:
        required = {"vendor_name", "invoice_date"}
        missing = required - set(value)
        if missing:
            raise ValueError(f"Missing required extracted fields: {sorted(missing)}")
        return value

    @field_validator("category")
    @classmethod
    def category_must_be_allowed(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value

        # Support optional top-2 encoding as "CategoryA|CategoryB" or "CategoryA,CategoryB".
        tokens = [piece.strip() for piece in value.replace("|", ",").split(",") if piece.strip()]
        if not tokens:
            raise ValueError("category cannot be empty")
        if len(tokens) > 2:
            raise ValueError("category supports at most 2 ranked guesses")

        invalid = [item for item in tokens if item not in ALLOWED_CATEGORIES]
        if invalid:
            raise ValueError(f"category must be one of {sorted(ALLOWED_CATEGORIES)}")
        return value


class InvoiceReward(BaseModel):
    """Continuous reward object with a detailed breakdown."""

    score: float
    details: Dict[str, Any]

    @field_validator("score")
    @classmethod
    def score_must_be_between_zero_and_one(cls, value: float) -> float:
        if not 0.0 < value < 1.0:
            raise ValueError("score must be between 0.0 and 1.0")
        return value