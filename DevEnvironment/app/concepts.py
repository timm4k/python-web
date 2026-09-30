from collections.abc import Callable, Iterable, Iterator
from functools import wraps
from typing import Literal, TypedDict

CatCategory = Literal["anatomy", "behavior"]
CatAccent = Literal["violet", "pink", "blue", "lime", "orange"]


class CatFact(TypedDict):
    id: int
    title: str
    fact: str
    category: CatCategory
    accent: CatAccent


class ConceptExample(TypedDict):
    name: str
    expression: str
    result: str


CAT_FACTS: tuple[CatFact, ...] = (
    {
        "id": 1,
        "title": "Built-in compass",
        "fact": (
            "A cat's whiskers help it estimate whether its body can fit through a narrow space"
        ),
        "category": "anatomy",
        "accent": "violet",
    },
    {
        "id": 2,
        "title": "Quiet communication",
        "fact": "Slow blinking is commonly used by relaxed cats during friendly interactions",
        "category": "behavior",
        "accent": "pink",
    },
    {
        "id": 3,
        "title": "A serious nap schedule",
        "fact": "Cats often sleep for twelve to sixteen hours during a single day",
        "category": "behavior",
        "accent": "blue",
    },
    {
        "id": 4,
        "title": "High-frequency hearing",
        "fact": "Cats can hear frequencies far above the upper range of human hearing",
        "category": "anatomy",
        "accent": "lime",
    },
    {
        "id": 5,
        "title": "Unique nose pattern",
        "fact": "The pattern of ridges on a cat's nose is individual, much like a fingerprint",
        "category": "anatomy",
        "accent": "orange",
    },
    {
        "id": 6,
        "title": "Tail as a signal",
        "fact": "A raised tail often signals a confident and friendly greeting",
        "category": "behavior",
        "accent": "violet",
    },
)


def iter_cat_facts(category: CatCategory | None = None) -> Iterator[CatFact]:
    for fact in CAT_FACTS:
        if category is None or fact["category"] == category:
            yield fact


def create_fact_filter(keyword: str) -> Callable[[CatFact], bool]:
    normalized_keyword = keyword.strip().casefold()

    def matches(fact: CatFact) -> bool:
        searchable_text = f"{fact['title']} {fact['fact']} {fact['category']}".casefold()
        return normalized_keyword in searchable_text

    return matches


def decorate_fact(function: Callable[[], str]) -> Callable[[], str]:
    @wraps(function)
    def wrapper() -> str:
        return f"Purr-reviewed: {function()}"

    return wrapper


@decorate_fact
def featured_message() -> str:
    return CAT_FACTS[0]["fact"]


def query_cat_facts(
    category: CatCategory | None = None,
    keyword: str | None = None,
    sort_by_title: bool = False,
) -> list[CatFact]:
    facts: Iterable[CatFact] = iter_cat_facts(category)
    if keyword is not None:
        facts = filter(create_fact_filter(keyword), facts)
    if sort_by_title:
        return sorted(facts, key=lambda fact: fact["title"])
    return list(facts)


def get_sorted_facts() -> list[CatFact]:
    return query_cat_facts(sort_by_title=True)


def find_facts(keyword: str) -> list[CatFact]:
    return query_cat_facts(keyword=keyword)


def get_concept_examples() -> list[ConceptExample]:
    anatomy_count = sum(1 for fact in iter_cat_facts("anatomy"))
    return [
        {"name": "Tuple", "expression": "CAT_FACTS[0]", "result": CAT_FACTS[0]["title"]},
        {
            "name": "Dictionary",
            "expression": "fact['category']",
            "result": CAT_FACTS[1]["category"],
        },
        {
            "name": "Lambda",
            "expression": "sorted(key=lambda fact: fact['title'])",
            "result": get_sorted_facts()[0]["title"],
        },
        {
            "name": "Generator",
            "expression": "sum(1 for fact in iter_cat_facts('anatomy'))",
            "result": str(anatomy_count),
        },
        {
            "name": "Closure",
            "expression": "create_fact_filter('whiskers')",
            "result": find_facts("whiskers")[0]["title"],
        },
        {"name": "Decorator", "expression": "@decorate_fact", "result": featured_message()},
    ]
