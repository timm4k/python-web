import importlib.metadata

from app.environment import read_runtime_environment


def package_version(package_name: str) -> str:
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return "not installed"


def main() -> None:
    runtime = read_runtime_environment()
    checks = {
        "Python": runtime.python_version,
        "pip": package_version("pip"),
        "Ruff": package_version("ruff"),
        "mypy": package_version("mypy"),
        "FastAPI": package_version("fastapi"),
        "Virtual environment": "active" if runtime.virtual_environment else "inactive",
        "Operating system": runtime.operating_system,
        "Architecture": runtime.architecture,
    }
    width = max(len(name) for name in checks)
    print("PURRFECT PYTHON ENVIRONMENT")
    print("=" * (width + 24))
    for name, value in checks.items():
        print(f"{name:<{width}}  {value}")


if __name__ == "__main__":
    main()
