from pydantic import BaseModel, Field
from typing import Optional


class Expense(BaseModel):
    amount: Optional[float] = Field(
        default=None,
        description="Expense amount"
    )
    category: Optional[str] = Field(
        default=None,
        description="Expense category like Food, Travel, Shopping"
    )
    merchant: Optional[str] = Field(
        default=None,
        description="Merchant or place"
    )
    date: Optional[str] = Field(
        default=None,
        description="Date in YYYY-MM-DD format"
    )
    notes: Optional[str] = Field(
        default=None,
        description="Extra notes"
    )