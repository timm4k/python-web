class A:
    pass


class B(A):
    pass


class C(A):
    pass


class D(B, C):
    pass


class E(C):
    pass


class F(D, E):
    pass


CLASSES = (A, B, C, D, E, F)

# L(F) = F + merge(L(D), L(E), [D, E])
# D is selected first, then B, then E cus C still appears in E's tail
# C becomes available after E, followed by A and object ^_^
MANUAL_F_MRO = ("F", "D", "B", "E", "C", "A", "object")


def inconsistent_mro_error() -> str:
    try:
        type("X", (A, B), {})
    except TypeError as error:
        return str(error)
    raise RuntimeError("The inconsistent hierarchy unexpectedly succeeded")


def main() -> None:
    for class_type in CLASSES:
        print(f"{class_type.__name__}: {[item.__name__ for item in class_type.__mro__]}")
    print(f"Manual F MRO: {list(MANUAL_F_MRO)}")
    print(f"C3 result matches: {MANUAL_F_MRO == tuple(cls.__name__ for cls in F.__mro__)}")
    print(f"Inconsistent hierarchy: {inconsistent_mro_error()}")


if __name__ == "__main__":
    main()
