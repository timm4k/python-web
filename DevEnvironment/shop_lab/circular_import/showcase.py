import subprocess
import sys
from pathlib import Path

PROJECT_DIRECTORY = Path(__file__).resolve().parents[2]
BROKEN_MODULE = "shop_lab.circular_import.broken.main"
FIXED_MODULE = "shop_lab.circular_import.fixed.main"
PROCESS_TIMEOUT_SECONDS = 10


def run_module(module_name: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", module_name],
        cwd=PROJECT_DIRECTORY,
        capture_output=True,
        check=False,
        text=True,
        timeout=PROCESS_TIMEOUT_SECONDS,
    )


def main() -> None:
    broken_result = run_module(BROKEN_MODULE)
    print("BROKEN CIRCULAR IMPORT")
    print(broken_result.stderr.strip())

    fixed_result = run_module(FIXED_MODULE)
    print("\nFIXED DEPENDENCY DESIGN")
    print(fixed_result.stdout.strip())


if __name__ == "__main__":
    main()
