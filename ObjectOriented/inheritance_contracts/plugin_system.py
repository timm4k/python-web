import json
from abc import ABC, abstractmethod


class BaseExporter(ABC):
    @abstractmethod
    def export(self, data: dict[str, object]) -> str:
        raise NotImplementedError

    @classmethod
    def get_format_name(cls) -> str:
        return cls.__name__.removesuffix("Exporter").lower()


class JsonExporter(BaseExporter):
    def export(self, data: dict[str, object]) -> str:
        return json.dumps(data, indent=2)


class CsvExporter(BaseExporter):
    def export(self, data: dict[str, object]) -> str:
        return ",".join(f"{key}={value}" for key, value in data.items())


class YamlExporter(BaseExporter):
    def export(self, data: dict[str, object]) -> str:
        return "\n".join(f"{key}: {value}" for key, value in data.items())


def get_all_exporters() -> list[type[BaseExporter]]:
    return BaseExporter.__subclasses__()


def export_data(data: dict[str, object], format_name: str) -> str:
    normalized_format = format_name.strip().casefold()
    exporter_type = next(
        (
            candidate
            for candidate in get_all_exporters()
            if candidate.get_format_name() == normalized_format
        ),
        None,
    )
    if exporter_type is None:
        raise ValueError(f"Unsupported export format: {format_name}")
    return exporter_type().export(data)


def main() -> None:
    perfume: dict[str, object] = {
        "name": "Violet Archive",
        "family": "powdery floral",
        "price": 2800,
    }
    formats = [exporter.get_format_name() for exporter in get_all_exporters()]
    print(f"Available formats: {formats}")
    for format_name in formats:
        print(f"\n{format_name.upper()}\n{export_data(perfume, format_name)}")


if __name__ == "__main__":
    main()
