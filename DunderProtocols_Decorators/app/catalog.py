from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProtocolGuide:
    label: str
    file_name: str
    methods: tuple[str, ...]
    meaning: str
    outcome: str


PROTOCOL_GUIDES = (
    ProtocolGuide(
        "Identity and ordering",
        "movies.py",
        ("__repr__", "__str__", "__eq__", "__hash__", "__lt__"),
        "One object can have a developer view, a reader view and stable identity rules",
        "Movie works with repr, str, sorted, set and dict without special helper functions",
    ),
    ProtocolGuide(
        "Container behavior",
        "movie_collection.py",
        ("__len__", "__bool__", "__getitem__", "__contains__", "__iter__", "__add__"),
        "Python syntax delegates to methods implemented by MovieCollection",
        "The custom class behaves like a familiar built-in collection",
    ),
    ProtocolGuide(
        "Alternative construction",
        "movie_factories.py",
        ("@classmethod", "@staticmethod"),
        "Factories parse external data through cls while validation stays independent of state",
        "The same factory creates Movie or PremiumMovie polymorphically",
    ),
    ProtocolGuide(
        "Function lifecycle",
        "decorators_demo.py",
        ("@timed", "@retry", "@wraps"),
        "Decorators add timing and retry behavior around a function call",
        "The original name and documentation survive the wrapper stack",
    ),
    ProtocolGuide(
        "Managed object lifecycle",
        "context_demo.py",
        ("__call__", "__enter__", "__exit__"),
        "A class decorator preserves one cache while a context manager brackets a session",
        "Initialization, work, cleanup and errors follow an explicit sequence",
    ),
)
