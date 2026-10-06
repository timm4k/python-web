from collections.abc import Callable

from cinema_protocols import (
    context_demo,
    decorators_demo,
    movie_collection,
    movie_factories,
    movies,
)

Showcase = tuple[str, Callable[[], None]]

SHOWCASES: tuple[Showcase, ...] = (
    ("REPRESENTATION, COMPARISON AND HASHING", movies.main),
    ("CONTAINER PROTOCOL", movie_collection.main),
    ("ALTERNATIVE CONSTRUCTORS", movie_factories.main),
    ("FUNCTION DECORATORS", decorators_demo.main),
    ("CLASS DECORATOR AND CONTEXT MANAGER", context_demo.main),
)


def separator(title: str) -> None:
    print(f"\n{'=' * 68}\n{title}\n{'=' * 68}")


def main() -> None:
    for title, run in SHOWCASES:
        separator(title)
        run()
    separator("DUNDER PROTOCOLS AND DECORATORS SHOWCASE COMPLETE")


if __name__ == "__main__":
    main()
