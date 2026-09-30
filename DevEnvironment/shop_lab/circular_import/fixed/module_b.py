from shop_lab.circular_import.fixed.names import get_a_name


def run() -> str:
    return f"Running B and calling A: {get_a_name()}"
