from collections.abc import Callable

from object_model import (
    calculator,
    car_model,
    config,
    library,
    object_lifecycle,
    products,
    slots_perf,
    teams,
    vault,
)

SHOWCASES: tuple[tuple[str, Callable[[], None]], ...] = (
    ("BOOK CLASS AND INSTANCES", library.main),
    ("CLASS AND INSTANCE ATTRIBUTES", teams.main),
    ("BOUND AND UNBOUND METHODS", calculator.main),
    ("OBJECT LIFECYCLE", object_lifecycle.main),
    ("SINGLETON SETTINGS", config.main),
    ("SLOTS AND MEMORY", slots_perf.main),
    ("ENCAPSULATION AND NAME MANGLING", vault.main),
    ("VALIDATED PROPERTY", products.main),
    ("REUSABLE DESCRIPTOR", car_model.main),
)


def print_section(title: str) -> None:
    print(f"\n{'=' * 64}\n{title}\n{'=' * 64}")


def main() -> None:
    for title, showcase in SHOWCASES:
        print_section(title)
        showcase()
    print_section("OBJECT MODEL SHOWCASE COMPLETE")


if __name__ == "__main__":
    main()
