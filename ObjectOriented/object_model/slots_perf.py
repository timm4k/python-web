import sys
import tracemalloc
from collections.abc import Callable


class RegularPoint:
    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z


class SlottedPoint:
    __slots__ = ("x", "y", "z")

    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z


def measure_peak_memory[PointType: (RegularPoint, SlottedPoint)](
    factory: Callable[[float, float, float], PointType], count: int
) -> int:
    if count < 1:
        raise ValueError("Point count must be positive")
    tracemalloc.start()
    points = [factory(index, index * 2, index * 3) for index in range(count)]
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del points
    return peak


def main() -> None:
    regular = RegularPoint(1, 2, 3)
    slotted = SlottedPoint(1, 2, 3)
    regular_size = sys.getsizeof(regular) + sys.getsizeof(regular.__dict__)
    slotted_size = sys.getsizeof(slotted)
    print(f"RegularPoint footprint: {regular_size} bytes")
    print(f"SlottedPoint footprint: {slotted_size} bytes")
    regular_peak = measure_peak_memory(RegularPoint, 100_000)
    slotted_peak = measure_peak_memory(SlottedPoint, 100_000)
    print(f"RegularPoint peak memory: {regular_peak / 1024 / 1024:.2f} MB")
    print(f"SlottedPoint peak memory: {slotted_peak / 1024 / 1024:.2f} MB")
    color_attribute = "color"
    setattr(regular, color_attribute, "red")
    print(f"RegularPoint dynamic color: {getattr(regular, color_attribute)}")
    try:
        setattr(slotted, color_attribute, "red")
    except AttributeError as error:
        print(f"SlottedPoint dynamic attribute: {error}")


if __name__ == "__main__":
    main()
