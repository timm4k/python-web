from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.service_config import VALID_CONFIG, ServiceConfig


def test_valid_config_masks_secrets() -> None:
    config = ServiceConfig.model_validate(VALID_CONFIG)

    assert str(config.secret_key) == "**********"
    assert str(config.database.credentials.password) == "**********"


def test_production_forces_debug_off() -> None:
    payload = deepcopy(VALID_CONFIG)
    payload["debug_mode"] = True

    config = ServiceConfig.model_validate(payload)

    assert config.debug_mode is False


@pytest.mark.parametrize(
    ("field", "value"),
    [("admin_emails", ["invalid"]), ("secret_key", "short")],
)
def test_invalid_config_is_rejected(field: str, value: object) -> None:
    payload = deepcopy(VALID_CONFIG)
    payload[field] = value

    with pytest.raises(ValidationError):
        ServiceConfig.model_validate(payload)
