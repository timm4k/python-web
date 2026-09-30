import importlib
import sys
from pathlib import Path
from types import ModuleType

from shop_lab.module_lab import utilities

MODULE_DIRECTORY = Path(__file__).resolve().parent
EXTRA_LIBS_DIRECTORY = MODULE_DIRECTORY / "extra_libs"
CURRENT_DIRECTORY = Path.cwd().resolve()


def load_helper() -> ModuleType:
    sys.modules.pop("helper", None)
    try:
        importlib.import_module("helper")
    except ModuleNotFoundError as error:
        print(f"Direct helper import failed as expected: {error.name}")

    extra_path = str(EXTRA_LIBS_DIRECTORY)
    sys.path.insert(0, extra_path)
    try:
        return importlib.import_module("helper")
    finally:
        sys.path.remove(extra_path)


def main() -> None:
    print(f"sys.path type: {type(sys.path).__name__}")
    print("sys.path entries:")
    for path_entry in sys.path:
        print(f"  {path_entry or CURRENT_DIRECTORY}")
    resolved_paths = {Path(path or CURRENT_DIRECTORY).resolve() for path in sys.path}
    print(f"Current project directory: {CURRENT_DIRECTORY}")
    print(f"Current directory found: {CURRENT_DIRECTORY in resolved_paths}")
    module_name = "shop_lab.module_lab.utilities"
    print(f"utilities cached in sys.modules: {module_name in sys.modules}")
    print(f"VAT rate from utilities: {utilities.VAT_RATE:.0%}")
    helper = load_helper()
    print(helper.say_hello())


if __name__ == "__main__":
    main()
