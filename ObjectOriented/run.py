import os

import uvicorn


def get_port() -> int:
    raw_port = os.getenv("PERFUME_LAB_PORT", "8000")
    try:
        port = int(raw_port)
    except ValueError as error:
        raise SystemExit("PERFUME_LAB_PORT must be a number") from error
    if port not in range(1024, 65536):
        raise SystemExit("PERFUME_LAB_PORT must be between 1024 and 65535")
    return port


def main() -> None:
    uvicorn.run(
        "app.main:app",
        host=os.getenv("PERFUME_LAB_HOST", "127.0.0.1"),
        port=get_port(),
        reload=os.getenv("PERFUME_LAB_RELOAD", "false").lower() == "true",
    )


if __name__ == "__main__":
    main()
