from app.concepts import find_facts, get_concept_examples, iter_cat_facts


def test_generator_filters_category() -> None:
    facts = list(iter_cat_facts("behavior"))
    assert facts
    assert all(fact["category"] == "behavior" for fact in facts)


def test_closure_filters_keyword() -> None:
    facts = find_facts("whiskers")
    assert len(facts) == 1
    assert facts[0]["title"] == "Built-in compass"


def test_all_requested_concepts_are_demonstrated() -> None:
    names = {example["name"] for example in get_concept_examples()}
    assert names == {"Tuple", "Dictionary", "Lambda", "Generator", "Closure", "Decorator"}
