from typing import TypedDict


class ConceptSummary(TypedDict):
    index: int
    title: str
    focus: str
    demonstration: str
    meaning: str
    module: str
    command: str


type ConceptDefinition = tuple[str, str, str, str, str]


def build_concepts(
    package: str,
    definitions: tuple[ConceptDefinition, ...],
) -> tuple[ConceptSummary, ...]:
    return tuple(
        {
            "index": index,
            "title": title,
            "focus": focus,
            "demonstration": demonstration,
            "meaning": meaning,
            "module": f"{module}.py",
            "command": f"python -m {package}.{module}",
        }
        for index, (module, title, focus, demonstration, meaning) in enumerate(definitions, start=1)
    )
