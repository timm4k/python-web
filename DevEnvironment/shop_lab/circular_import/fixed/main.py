from shop_lab.circular_import.fixed import module_a, module_b


def main() -> None:
    print(module_a.run())
    print(module_b.run())


if __name__ == "__main__":
    main()
