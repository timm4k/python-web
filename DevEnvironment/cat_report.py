from app.concepts import get_sorted_facts
from app.environment import read_runtime_environment


def calculate_factorial(number: int) -> int:
    result = 1
    for value in range(1, number + 1):
        result *= value
    return result


def main() -> None:
    visitor_name = input("What is your name? ").strip() or "Python explorer"
    facts = get_sorted_facts()
    runtime = read_runtime_environment()
    print(f"\nWelcome to the cat lab, {visitor_name}!")
    print(f"Python: {runtime.python_version}")
    print(f"System: {runtime.operating_system}")
    print(f"Architecture: {runtime.architecture}")
    status = "active" if runtime.virtual_environment else "inactive"
    print(f"Virtual environment: {status}")
    print(f"Five factorial: {calculate_factorial(5)}")
    print("\nThree purr-reviewed facts:")
    for index, fact in enumerate(facts[:3], start=1):
        print(f"{index}. {fact['title']}: {fact['fact']}")


if __name__ == "__main__":
    main()
