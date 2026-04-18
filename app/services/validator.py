from typing import Optional, Tuple
from app.schemas.state import ValidationError

ALLOWED_CATEGORIES = {
    "Food",
    "Transport",
    "Shopping",
    "Bills",
    "Entertainment",
    "Health",
    "Grocery",
    "Other",
}


def validate_expense_data(expense) -> Tuple[bool, Optional[ValidationError]]:
    if expense is None:
        return False, ValidationError(
            type="no_data",
            message="I couldn't extract the expense details."
        )

    if expense.amount is None:
        return False, ValidationError(
            type="missing_amount",
            message="I couldn't detect the amount."
        )

    if expense.amount <= 0:
        return False, ValidationError(
            type="invalid_amount",
            message="Amount must be greater than zero."
        )

    if not expense.category:
        return False, ValidationError(
            type="missing_category",
            message="I couldn't detect the category."
        )

    
    category = expense.category.title()

    if category not in ALLOWED_CATEGORIES:
        return False, ValidationError(
            type="invalid_category",
            message=f"{category} is not a valid category."
        )

    return True, None