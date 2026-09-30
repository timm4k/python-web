from shop_lab.shop import __version__, create_order, format_customer_info, get_product


def main() -> None:
    print(f"CAT SHOP PACKAGE {__version__}")
    print(format_customer_info("Tate", "TATE@EXAMPLE.COM"))
    product = get_product(2)
    if product is not None:
        print(f"Selected product: {product['name']}")
    create_order("Tate", 2)


if __name__ == "__main__":
    main()
