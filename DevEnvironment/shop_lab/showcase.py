import json
import subprocess
import sys
from pathlib import Path

from shop_lab import main as package_demo
from shop_lab.circular_import.showcase import BROKEN_MODULE, FIXED_MODULE, run_module
from shop_lab.module_lab import app as import_demo
from shop_lab.module_lab import inspector, math_ops, utilities
from shop_lab.order_simulator import ORDERS_FILE, generate_orders, save_orders
from shop_lab.shop import __version__, format_customer_info, get_product
from shop_lab.shop.orders.processing import build_order_message

PROJECT_DIRECTORY = Path(__file__).resolve().parent.parent
PROCESSING_SCRIPT = PROJECT_DIRECTORY / "shop_lab" / "shop" / "orders" / "processing.py"
PROCESS_TIMEOUT_SECONDS = 10
IGNORED_DIRECTORIES = frozenset({"__pycache__", ".venv", "generated"})


def print_section(title: str) -> None:
    print(f"\n{'=' * 64}\n{title}\n{'=' * 64}")


def run_script(path: Path, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(path)],
        cwd=PROJECT_DIRECTORY,
        input=input_text,
        capture_output=True,
        check=False,
        text=True,
        timeout=PROCESS_TIMEOUT_SECONDS,
    )


def last_error_line(result: subprocess.CompletedProcess[str]) -> str:
    return next(
        (line.strip() for line in reversed(result.stderr.splitlines()) if line.strip()),
        "No error output",
    )


def show_package_structure() -> None:
    print_section("PACKAGE STRUCTURE")
    package_directory = Path(__file__).resolve().parent
    for directory in sorted(path for path in package_directory.iterdir() if path.is_dir()):
        if directory.name in IGNORED_DIRECTORIES:
            continue
        entries = sorted(
            path.name + ("/" if path.is_dir() else "")
            for path in directory.iterdir()
            if path.name not in IGNORED_DIRECTORIES
        )
        print(f"{directory.name}/: {', '.join(entries)}")
    root_modules = sorted(path.name for path in package_directory.glob("*.py"))
    print(f"root modules: {', '.join(root_modules)}")


def show_imports() -> None:
    print_section("CUSTOM MODULE AND THREE IMPORT STYLES")
    import_demo.main()
    print(f"VAT constant: {utilities.VAT_RATE:.0%}")
    print(f"utilities cached in sys.modules: {'shop_lab.module_lab.utilities' in sys.modules}")
    print(f"sys.path type: {type(sys.path).__name__}")
    print(f"Search locations: {len(sys.path)}")
    helper = inspector.load_helper()
    print(helper.say_hello())


def show_entry_point() -> None:
    print_section("ENTRY POINT AND SAFE IMPORT")
    direct_run = run_script(Path(math_ops.__file__), "12.5\n")
    print(direct_run.stdout.strip())
    print("math_ops imported without starting interactive input")
    print(f"double(12.5): {math_ops.double(12.5):g}")


def show_dependency_design() -> None:
    print_section("CIRCULAR IMPORT AND FIXED DEPENDENCY DESIGN")
    broken_result = run_module(BROKEN_MODULE)
    fixed_result = run_module(FIXED_MODULE)
    print(f"Broken design: {last_error_line(broken_result)}")
    print("Fixed design:")
    print(fixed_result.stdout.strip())


def show_package() -> None:
    print_section("PACKAGE FACADE AND RELATIVE IMPORT")
    print(f"Package version: {__version__}")
    print(format_customer_info("Tate", "TATE@EXAMPLE.COM"))
    product = get_product(2)
    if product is not None:
        print(f"Selected product: {product['name']} · {product['price']:.2f} UAH")
    print(build_order_message("Tate", 2))
    direct_run = run_script(PROCESSING_SCRIPT)
    print(f"Direct relative-import run: {last_error_line(direct_run)}")
    print("Package-aware run:")
    package_demo.main()


def show_order_manifest() -> None:
    print_section("RANDOM ORDERS AND JSON MANIFEST")
    orders = generate_orders()
    output_path = save_orders(orders)
    print(f"Generated records: {len(orders)}")
    print(f"JSON file: {output_path.relative_to(PROJECT_DIRECTORY)}")
    print("First two records:")
    print(json.dumps(orders[:2], indent=2))


def main() -> None:
    show_package_structure()
    show_imports()
    show_entry_point()
    show_dependency_design()
    show_package()
    show_order_manifest()
    print_section("SHOWCASE COMPLETE")
    print(f"Full five-order manifest: {ORDERS_FILE.relative_to(PROJECT_DIRECTORY)}")


if __name__ == "__main__":
    main()
