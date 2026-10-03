class Calculator:
    def add(self, first: float, second: float) -> float:
        return first + second


def main() -> None:
    calculator = Calculator()
    print(f"Bound call: {calculator.add(10, 5):g}")
    print(f"Unbound call: {Calculator.add(calculator, 10, 5):g}")
    print(f"Bound type: {type(calculator.add).__name__}")
    print(f"Class attribute type: {type(Calculator.add).__name__}")


if __name__ == "__main__":
    main()
