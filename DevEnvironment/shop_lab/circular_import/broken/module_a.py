from shop_lab.circular_import.broken import module_b


def get_a_name() -> str:
    return "Module A"


def run() -> str:
    return f"Running A and calling B: {module_b.get_b_name()}"
