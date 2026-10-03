import types

import pytest

from object_model.calculator import Calculator
from object_model.car_model import Car, NonNegativeNumber
from object_model.config import AppSettings
from object_model.library import Book
from object_model.object_lifecycle import TracedObject, create_invalid_initializer
from object_model.products import Product
from object_model.slots_perf import RegularPoint, SlottedPoint, measure_peak_memory
from object_model.teams import BrokenTeam, CorrectTeam
from object_model.vault import SecureVault


def test_book_representation_discount_and_dynamic_attribute() -> None:
    book = Book("Perfume", "Patrick Suskind", 272, 400)
    assert repr(book) == "Book(title='Perfume', author='Patrick Suskind', price=400.0)"
    book.apply_discount(15)
    genre_attribute = "genre"
    setattr(book, genre_attribute, "Literary fiction")
    assert book.price == 340
    assert getattr(book, genre_attribute) == "Literary fiction"


@pytest.mark.parametrize("discount", [-1, 101, float("inf")])
def test_book_rejects_invalid_discount(discount: float) -> None:
    book = Book("Perfume", "Patrick Suskind", 272, 400)
    with pytest.raises(ValueError):
        book.apply_discount(discount)


def test_mutable_class_attribute_problem_and_instance_fix() -> None:
    BrokenTeam.members.clear()
    broken_a = BrokenTeam("Perfumers")
    broken_b = BrokenTeam("Designers")
    broken_a.add_member("Elena")
    assert broken_b.members == ["Elena"]

    correct_a = CorrectTeam("Perfumers")
    correct_b = CorrectTeam("Designers")
    correct_a.add_member("Elena")
    assert correct_a.members == ["Elena"]
    assert correct_b.members == []


def test_bound_and_unbound_method_calls() -> None:
    calculator = Calculator()
    assert calculator.add(10, 5) == 15
    assert Calculator.add(calculator, 10, 5) == 15
    assert isinstance(calculator.add, types.MethodType)
    assert isinstance(Calculator.add, types.FunctionType)


def test_object_lifecycle_and_invalid_initializer(capsys: pytest.CaptureFixture[str]) -> None:
    traced = TracedObject("Test")
    output = capsys.readouterr().out
    assert traced.name == "Test"
    assert output.index("__new__") < output.index("__init__")
    with pytest.raises(TypeError, match="__init__.*None"):
        create_invalid_initializer()()


def test_singleton_preserves_first_configuration() -> None:
    first = AppSettings("postgresql://localhost/perfume", debug=True)
    second = AppSettings("mysql://production/perfume", debug=False)
    assert first is second
    assert second.database_url == "postgresql://localhost/perfume"
    assert second.debug is True


def test_slots_reduce_peak_memory_and_prevent_dynamic_attributes() -> None:
    regular_peak = measure_peak_memory(RegularPoint, 2_000)
    slotted_peak = measure_peak_memory(SlottedPoint, 2_000)
    assert slotted_peak < regular_peak
    regular = RegularPoint(1, 2, 3)
    color_attribute = "color"
    setattr(regular, color_attribute, "red")
    assert getattr(regular, color_attribute) == "red"
    with pytest.raises(AttributeError):
        setattr(SlottedPoint(1, 2, 3), color_attribute, "red")


def test_name_mangling_exposes_private_storage_without_security() -> None:
    vault = SecureVault("Alexander")
    assert vault.owner == "Alexander"
    assert vault._location == "Swiss archive"
    with pytest.raises(AttributeError):
        getattr(vault, "__passcode")
    mangled_name = "_SecureVault__passcode"
    assert getattr(vault, mangled_name) == "1234-5678-super-secret"


def test_property_validates_and_protects_price() -> None:
    perfume = Product("Violet Archive", 2800)
    assert perfume.price == 2800
    price_attribute = "price"
    with pytest.raises(TypeError):
        setattr(perfume, price_attribute, "expensive")
    with pytest.raises(ValueError):
        perfume.price = -1
    with pytest.raises(AttributeError):
        del perfume.price


def test_descriptor_validates_multiple_fields() -> None:
    car = Car("Toyota", 15_000, 50)
    assert car.mileage == 15_000
    assert car.fuel_capacity == 50
    assert isinstance(Car.mileage, NonNegativeNumber)
    with pytest.raises(ValueError):
        car.mileage = -100
    capacity_attribute = "fuel_capacity"
    with pytest.raises(TypeError):
        setattr(car, capacity_attribute, "full tank")
