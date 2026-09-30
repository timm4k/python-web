from shop_lab.module_lab import math_ops


def main() -> None:
    print("math_ops imported without starting interactive input")
    print(f"math_ops.__name__: {math_ops.__name__}")
    print(f"double(12.5): {math_ops.double(12.5):g}")


if __name__ == "__main__":
    main()
