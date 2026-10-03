from collections.abc import Callable

from inheritance_contracts import (
    cooperative,
    data_store,
    hierarchy,
    mro_calc,
    notifications,
    plugin_system,
    protocols_demo,
    serializers,
    vehicles,
)

SHOWCASES: tuple[tuple[str, Callable[[], None]], ...] = (
    ("INHERITANCE AND POLYMORPHISM", vehicles.main),
    ("HIERARCHY INTROSPECTION", hierarchy.main),
    ("COOPERATIVE SUPER", cooperative.main),
    ("C3 METHOD RESOLUTION ORDER", mro_calc.main),
    ("ABSTRACT NOTIFIER CONTRACT", notifications.main),
    ("ADVANCED ABSTRACT MEMBERS", data_store.main),
    ("STRUCTURAL PROTOCOLS", protocols_demo.main),
    ("ABC AND PROTOCOL COMPOSITION", serializers.main),
    ("DYNAMIC EXPORTER PLUGINS", plugin_system.main),
)


def print_section(title: str) -> None:
    print(f"\n{'=' * 64}\n{title}\n{'=' * 64}")


def main() -> None:
    for title, showcase in SHOWCASES:
        print_section(title)
        showcase()
    print_section("INHERITANCE AND CONTRACTS SHOWCASE COMPLETE")


if __name__ == "__main__":
    main()
