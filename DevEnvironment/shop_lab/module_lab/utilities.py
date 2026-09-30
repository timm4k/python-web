import math

VAT_RATE = 0.20


def _validate_amount(amount: float) -> None:
    if not math.isfinite(amount) or amount < 0:
        raise ValueError("Amount must be a finite non-negative number")


def calculate_vat(price: float) -> float:
    _validate_amount(price)
    return round(price * VAT_RATE, 2)


def format_currency(amount: float) -> str:
    _validate_amount(amount)
    return f"{amount:,.2f} UAH"
