from ..catalog import get_product


def build_order_message(customer_name: str, product_id: int) -> str:
    normalized_name = customer_name.strip()
    if not normalized_name:
        raise ValueError("Customer name is required")
    product = get_product(product_id)
    if product is None:
        raise LookupError(f"Product {product_id} was not found")
    return f"Order created for {normalized_name}: {product['name']} for {product['price']:,.2f} UAH"


def create_order(customer_name: str, product_id: int) -> str:
    try:
        message = build_order_message(customer_name, product_id)
    except LookupError as error:
        message = str(error)
    print(message)
    return message
