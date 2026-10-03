import pytest

from inheritance_contracts.cooperative import Button, D
from inheritance_contracts.data_store import DataStore, PostgreSQLStore
from inheritance_contracts.hierarchy import all_subclasses
from inheritance_contracts.mro_calc import MANUAL_F_MRO, F, inconsistent_mro_error
from inheritance_contracts.notifications import (
    BaseNotifier,
    EmailNotifier,
    IncompleteNotifier,
    SmsNotifier,
)
from inheritance_contracts.plugin_system import export_data, get_all_exporters
from inheritance_contracts.protocols_demo import Circle, Drawable, EmailTransport, Square
from inheritance_contracts.serializers import InMemoryStorage, JsonSerializer, SimpleSerializer
from inheritance_contracts.vehicles import Car, ElectricCar, Vehicle, create_sample_vehicles


def instantiate(class_type: type[object]) -> object:
    return class_type()


def test_single_inheritance_override_and_polymorphism() -> None:
    vehicles = create_sample_vehicles()
    results = [vehicle.start_engine() for vehicle in vehicles]
    assert results[0] == "Atlas (2020) engine started"
    assert "Safety belts checked" in results[1]
    assert results[2] == "Tesla: silent start · charge 100%"


def test_hierarchy_introspection_finds_direct_and_recursive_children() -> None:
    tesla = ElectricCar("Tesla", 2024, 75)
    assert Vehicle.__subclasses__() == [Car]
    assert {Car, ElectricCar} <= all_subclasses(Vehicle)
    assert isinstance(tesla, (ElectricCar, Car, Vehicle, object))
    assert issubclass(ElectricCar, Vehicle)


def test_super_follows_mro_and_cooperative_initialization() -> None:
    assert [class_type.__name__ for class_type in D.__mro__] == ["D", "B", "C", "A", "object"]
    assert D().greet() == "D → B → C → A"
    button = Button(label="Blend", color="violet", on_click="compose")
    assert (button.label, button.color, button.on_click) == ("Blend", "violet", "compose")


def test_manual_c3_result_and_inconsistent_hierarchy() -> None:
    assert tuple(class_type.__name__ for class_type in F.__mro__) == MANUAL_F_MRO
    error = inconsistent_mro_error().replace("\n", " ")
    assert "consistent method resolution" in error
    assert "order (MRO)" in error


def test_abstract_contract_blocks_incomplete_implementations() -> None:
    with pytest.raises(TypeError):
        instantiate(BaseNotifier)
    with pytest.raises(TypeError):
        instantiate(IncompleteNotifier)
    notifier = EmailNotifier("smtp")
    assert notifier.send_bulk([1, 2], "Ready") == {1: True, 2: True}
    assert isinstance(notifier, BaseNotifier)
    assert BaseNotifier.__abstractmethods__ == frozenset({"send", "close"})
    assert EmailNotifier.__abstractmethods__ == frozenset()
    sms_notifier = SmsNotifier("Atelier")
    assert sms_notifier.send(3, "Shipped")
    sms_notifier.close()
    with pytest.raises(RuntimeError, match="Notifier is closed"):
        sms_notifier.send(3, "Duplicate")


def test_abstract_property_factory_validator_and_method() -> None:
    with pytest.raises(TypeError):
        instantiate(DataStore)
    config: dict[str, object] = {"host": "localhost", "db": "perfume"}
    assert PostgreSQLStore.validate_config(config)
    store = PostgreSQLStore.from_config(config)
    assert store.connection_string == "postgresql://localhost:5432/perfume"
    assert store.execute("SELECT 1") == []


def test_protocols_support_static_and_runtime_structural_typing() -> None:
    transport = EmailTransport()
    assert transport.send(42, "Ready")
    assert isinstance(Circle(), Drawable)
    assert not isinstance(Square(), Drawable)


def test_abc_storage_composes_with_protocol_serializers() -> None:
    json_storage = InMemoryStorage(JsonSerializer())
    json_storage.save("formula", {"note": "iris"})
    assert json_storage.load("formula") == {"note": "iris"}
    simple_storage = InMemoryStorage(SimpleSerializer())
    simple_storage.save("formula", "iris")
    assert simple_storage.load("formula") == "iris"
    assert simple_storage.load("missing") is None


def test_plugins_are_discovered_and_selected_by_format() -> None:
    formats = {exporter.get_format_name() for exporter in get_all_exporters()}
    assert formats == {"json", "csv", "yaml"}
    payload: dict[str, object] = {"name": "Violet Archive", "price": 2800}
    assert '"name": "Violet Archive"' in export_data(payload, "json")
    assert "name=Violet Archive" in export_data(payload, "csv")
    assert "name: Violet Archive" in export_data(payload, "yaml")
    with pytest.raises(ValueError):
        export_data(payload, "xml")
