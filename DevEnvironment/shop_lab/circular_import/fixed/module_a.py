from shop_lab.circular_import.fixed.names import get_b_name


def run() -> str:
    return f"Running A and calling B: {get_b_name()}"
