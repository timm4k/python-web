from pathlib import Path

import pytest
import requests

from shop_lab.circular_import.showcase import BROKEN_MODULE, FIXED_MODULE, run_module
from shop_lab.http_client.fetch_api import fetch_json
from shop_lab.module_lab.math_ops import double
from shop_lab.module_lab.utilities import VAT_RATE, calculate_vat, format_currency
from shop_lab.order_simulator import generate_orders, save_orders
from shop_lab.shop import __version__, create_order, format_customer_info, get_product


class FakeResponse:
    status_code = 200

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, object]:
        return {"origin": "127.0.0.1", "url": "https://httpbin.org/get"}


def test_utility_module_calculates_and_formats_vat() -> None:
    assert VAT_RATE == 0.20
    assert calculate_vat(120.50) == 24.10
    assert format_currency(120.50) == "120.50 UAH"


def test_math_module_can_be_imported_without_interactive_input() -> None:
    assert double(12.5) == 25


def test_circular_import_failure_and_fixed_design() -> None:
    broken_result = run_module(BROKEN_MODULE)
    fixed_result = run_module(FIXED_MODULE)
    assert broken_result.returncode != 0
    assert "partially initialized module" in broken_result.stderr
    assert fixed_result.returncode == 0
    assert "Running A and calling B: Module B" in fixed_result.stdout


def test_shop_facade_exposes_validated_operations(capsys: pytest.CaptureFixture[str]) -> None:
    assert __version__ == "1.0.0"
    assert get_product(2) == {"id": 2, "name": "Feather Wand", "price": 185.50}
    assert format_customer_info(" Tate ", "TATE@EXAMPLE.COM") == (
        "Customer: Tate (tate@example.com)"
    )
    message = create_order("Tate", 2)
    assert message == "Order created for Tate: Feather Wand for 185.50 UAH"
    assert message in capsys.readouterr().out


def test_http_client_validates_and_returns_json(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(url: str, timeout: int) -> FakeResponse:
        assert url == "https://httpbin.org/get"
        assert timeout == 10
        return FakeResponse()

    monkeypatch.setattr(requests, "get", fake_get)
    status_code, payload = fetch_json("https://httpbin.org/get")
    assert status_code == 200
    assert payload["origin"] == "127.0.0.1"


def test_order_simulator_writes_five_json_records(tmp_path: Path) -> None:
    orders = generate_orders()
    output_path = save_orders(orders, tmp_path / "orders.json")
    assert len(orders) == 5
    assert output_path.is_file()
    assert all(order["id"] == index for index, order in enumerate(orders, start=1))
