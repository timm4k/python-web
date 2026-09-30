def double(value: float) -> float:
    return value * 2


def main() -> None:
    raw_value = input("Enter a number to double: ").strip()
    try:
        value = float(raw_value)
    except ValueError:
        print("Enter a valid number")
        return
    print(f"Result: {double(value):g}")


if __name__ == "__main__":
    main()
