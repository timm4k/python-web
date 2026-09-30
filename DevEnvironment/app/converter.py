DIGITS = "0123456789ABCDEF"
SUPPORTED_BASES = frozenset({2, 10, 16})


def _ensure_supported_base(base: int) -> None:
    if base not in SUPPORTED_BASES:
        raise ValueError("Only binary, decimal and hexadecimal bases are supported")


def parse_number(raw_value: str, base: int) -> int:
    _ensure_supported_base(base)
    value = raw_value.strip().upper()
    if not value:
        raise ValueError("Enter a number to convert")
    sign = -1 if value.startswith("-") else 1
    digits = value[1:] if sign == -1 else value
    if not digits:
        raise ValueError("Enter at least one digit")
    allowed = DIGITS[:base]
    if any(character not in allowed for character in digits):
        raise ValueError(f"{raw_value} is not valid for base {base}")
    result = 0
    for character in digits:
        result = result * base + DIGITS.index(character)
    return sign * result


def format_number(number: int, base: int) -> str:
    _ensure_supported_base(base)
    if number == 0:
        return "0"
    sign = "-" if number < 0 else ""
    remaining = abs(number)
    result = ""
    while remaining > 0:
        result = DIGITS[remaining % base] + result
        remaining //= base
    return sign + result


def convert_number(value: str, from_base: int, to_base: int) -> str:
    return format_number(parse_number(value, from_base), to_base)


def decimal_to_binary(number: int) -> str:
    return format_number(number, 2)


def decimal_to_hex(number: int) -> str:
    return format_number(number, 16)


def binary_to_decimal(binary_value: str) -> int:
    return parse_number(binary_value, 2)
