import shop_lab.module_lab.utilities
import shop_lab.module_lab.utilities as utils
from shop_lab.module_lab.utilities import calculate_vat, format_currency

PRODUCT_PRICE = 125.50


def main() -> None:
    module_vat = shop_lab.module_lab.utilities.calculate_vat(PRODUCT_PRICE)
    direct_vat = calculate_vat(PRODUCT_PRICE)
    aliased_total = PRODUCT_PRICE + utils.calculate_vat(PRODUCT_PRICE)

    print("CAT SHOP VAT MODULE")
    print(f"Module import: {shop_lab.module_lab.utilities.format_currency(module_vat)}")
    print(f"Direct imports: {format_currency(direct_vat)}")
    print(f"Aliased module: {utils.format_currency(aliased_total)}")


if __name__ == "__main__":
    main()
