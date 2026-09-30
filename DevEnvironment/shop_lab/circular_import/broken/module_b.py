from shop_lab.circular_import.broken import module_a

A_NAME = module_a.get_a_name()


def get_b_name() -> str:
    return f"Module B connected to {A_NAME}"
