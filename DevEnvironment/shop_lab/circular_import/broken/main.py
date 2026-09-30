from shop_lab.circular_import.broken import module_a


def main() -> None:
    print(module_a.run())


if __name__ == "__main__":
    main()
