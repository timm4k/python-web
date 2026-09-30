import pytest

from app.converter import binary_to_decimal, convert_number, decimal_to_binary, decimal_to_hex


@pytest.mark.parametrize(
    ("number", "expected"),
    [(0, "0"), (5, "101"), (255, "11111111"), (-10, "-1010")],
)
def test_decimal_to_binary(number: int, expected: str) -> None:
    assert decimal_to_binary(number) == expected


def test_decimal_to_hex() -> None:
    assert decimal_to_hex(255) == "FF"


def test_binary_to_decimal() -> None:
    assert binary_to_decimal("10000000000") == 1024


def test_convert_between_supported_bases() -> None:
    assert convert_number("FF", 16, 2) == "11111111"


def test_invalid_digit_is_rejected() -> None:
    with pytest.raises(ValueError, match="not valid"):
        convert_number("102", 2, 10)
