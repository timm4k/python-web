import os
from urllib.parse import urlparse

import requests

DEFAULT_API_URL = "https://httpbin.org/get"
REQUEST_TIMEOUT_SECONDS = 10


def fetch_json(url: str) -> tuple[int, dict[str, object]]:
    parsed_url = urlparse(url)
    if parsed_url.scheme != "https" or not parsed_url.netloc:
        raise ValueError("API URL must use HTTPS")
    response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("API response must be a JSON object")
    return response.status_code, payload


def main() -> None:
    api_url = os.getenv("CAT_LAB_API_URL", DEFAULT_API_URL)
    try:
        status_code, payload = fetch_json(api_url)
    except (requests.RequestException, ValueError) as error:
        print(f"Request failed: {error}")
        return
    print(f"Status code: {status_code}")
    print(f"Response keys: {', '.join(sorted(payload))}")


if __name__ == "__main__":
    main()
