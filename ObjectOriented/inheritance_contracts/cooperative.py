class A:
    def greet(self) -> str:
        return "A"


class B(A):
    def greet(self) -> str:
        return f"B → {super().greet()}"


class C(A):
    def greet(self) -> str:
        return f"C → {super().greet()}"


class D(B, C):
    def greet(self) -> str:
        return f"D → {super().greet()}"


class CooperativeRoot:
    def __init__(self, **kwargs: str) -> None:
        if kwargs:
            unknown = ", ".join(sorted(kwargs))
            raise TypeError(f"Unknown arguments: {unknown}")
        super().__init__()


class GraphicElement(CooperativeRoot):
    def __init__(self, color: str = "black", **kwargs: str) -> None:
        super().__init__(**kwargs)
        self.color = color


class ClickableElement(CooperativeRoot):
    def __init__(self, on_click: str = "none", **kwargs: str) -> None:
        super().__init__(**kwargs)
        self.on_click = on_click


class Button(GraphicElement, ClickableElement):
    def __init__(self, label: str, **kwargs: str) -> None:
        super().__init__(**kwargs)
        self.label = label


def main() -> None:
    print(f"D MRO: {[cls.__name__ for cls in D.__mro__]}")
    print(f"Cooperative greeting: {D().greet()}")
    button = Button(label="Blend", color="violet", on_click="compose")
    print(f"Button: label={button.label}, color={button.color}, on_click={button.on_click}")
    print(f"Button MRO: {[cls.__name__ for cls in Button.__mro__]}")


if __name__ == "__main__":
    main()
