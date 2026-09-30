import platform
import sys
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RuntimeEnvironment:
    python_version: str
    operating_system: str
    architecture: str
    virtual_environment: bool


def read_runtime_environment() -> RuntimeEnvironment:
    return RuntimeEnvironment(
        python_version=platform.python_version(),
        operating_system=f"{platform.system()} {platform.release()}",
        architecture=platform.machine(),
        virtual_environment=sys.prefix != sys.base_prefix,
    )
