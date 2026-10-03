from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.concepts import ConceptSummary, build_concepts
from inheritance_contracts.cooperative import D
from inheritance_contracts.plugin_system import export_data, get_all_exporters
from inheritance_contracts.vehicles import ElectricCar, create_sample_vehicles

router = APIRouter(prefix="/api/contracts", tags=["Inheritance and Contracts"])


class ExportRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    family: str = Field(min_length=1, max_length=80)
    price: float = Field(ge=0, le=1_000_000)
    format: Literal["json", "csv", "yaml"]


CONTRACT_CONCEPTS = build_concepts(
    "inheritance_contracts",
    (
        (
            "vehicles",
            "Inheritance",
            "Overrides, super and polymorphism",
            "Calls start_engine on Vehicle, Car and ElectricCar through one shared interface",
            "A subclass can extend or replace inherited behavior without changing the caller",
        ),
        (
            "hierarchy",
            "Hierarchy",
            "Bases, subclasses and isinstance",
            "Reads __base__, __bases__, __mro__ and checks instance and subclass relationships",
            "Python can inspect the class tree and recognizes indirect "
            "ancestors during type checks",
        ),
        (
            "cooperative",
            "Cooperative super",
            "Diamond inheritance and keyword forwarding",
            "Runs a diamond greet chain and initializes mixin-like classes through shared kwargs",
            "super() follows MRO, so every cooperative class can participate exactly once",
        ),
        (
            "mro_calc",
            "C3 linearization",
            "Predictable method resolution order",
            "Compares a manually calculated F order with F.__mro__ and builds an invalid hierarchy",
            "C3 preserves local ordering and monotonicity or rejects an inconsistent class graph",
        ),
        (
            "notifications",
            "Abstract contracts",
            "ABC and protected instantiation",
            "Attempts to instantiate incomplete notifiers and uses complete email and SMS versions",
            "ABC prevents objects from existing until every required operation is implemented",
        ),
        (
            "data_store",
            "Abstract members",
            "Properties, factories and validators",
            "Builds PostgreSQLStore from configuration through abstract property and method forms",
            "An abstract contract can define construction, validation, state access and behavior",
        ),
        (
            "protocols_demo",
            "Protocols",
            "Structural typing and runtime checks",
            "Passes unrelated transports to one typed function and checks a runtime Drawable",
            "Protocol accepts compatible behavior without requiring explicit inheritance",
        ),
        (
            "serializers",
            "Composition",
            "ABC storage with protocol serializers",
            "Injects JSON and simple serializers into the same in-memory storage implementation",
            "Composition changes one responsibility without rebuilding or subclassing the storage",
        ),
        (
            "plugin_system",
            "Plugin registry",
            "Discovery through __subclasses__",
            "Discovers JSON, CSV and YAML exporters and selects one by its declared format name",
            "New imported exporter subclasses extend the system without changing selection logic",
        ),
    ),
)


@router.get("/overview")
def overview() -> tuple[ConceptSummary, ...]:
    return CONTRACT_CONCEPTS


@router.get("/mro")
def mro_graph() -> dict[str, list[str] | str]:
    return {
        "diamond": [class_type.__name__ for class_type in D.__mro__],
        "greeting": D().greet(),
        "vehicles": [class_type.__name__ for class_type in ElectricCar.__mro__],
    }


@router.get("/polymorphism")
def polymorphism() -> list[dict[str, str]]:
    return [
        {"type": type(vehicle).__name__, "result": vehicle.start_engine()}
        for vehicle in create_sample_vehicles()
    ]


@router.get("/formats")
def formats() -> list[str]:
    return [exporter.get_format_name() for exporter in get_all_exporters()]


@router.post("/export")
def export_perfume(request: ExportRequest) -> dict[str, str]:
    try:
        result = export_data(
            {"name": request.name, "family": request.family, "price": request.price},
            request.format,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"format": request.format, "result": result}
