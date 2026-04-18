from app.services.validator import validate_expense_data
from app.schemas.expense import Expense


def test_valid_expense():
    expense = Expense(
        amount=20,
        category="Food",
        merchant="Chipotle",
        date="2026-04-09"
    )

    is_valid, error = validate_expense_data(expense)

    assert is_valid is True
    assert error is None


def test_missing_amount():
    expense = Expense(
        amount=None,
        category="Food",
        merchant="Chipotle",
        date="2026-04-09"
    )

    is_valid, error = validate_expense_data(expense)

    assert is_valid is False
    assert error is not None
    assert error.type == "missing_amount"


def test_invalid_category():
    expense = Expense(
        amount=20,
        category="Random",
        merchant="Test",
        date="2026-04-09"
    )

    is_valid, error = validate_expense_data(expense)

    assert is_valid is False
    assert error is not None
    assert error.type == "invalid_category"