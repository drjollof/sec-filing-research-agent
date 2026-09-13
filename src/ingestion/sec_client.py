import time
import requests

from src.config import (
    SEC_REQUESTS_PER_SECOND,
    SEC_USER_AGENT,
)


class SECClient:
    """HTTP client for interacting with SEC EDGAR APIs."""

    def __init__(self):
        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": SEC_USER_AGENT,
                "Accept": "application/json",
            }
        )

        self.min_request_interval = (
            1 / SEC_REQUESTS_PER_SECOND
        )

        self.last_request_time = 0.0

    def _throttle(self):
        """Ensure requests are spaced according to our rate limit."""

        elapsed = time.monotonic() - self.last_request_time

        if elapsed < self.min_request_interval:
            time.sleep(
                self.min_request_interval - elapsed
            )

    def get_json(
        self,
        url: str,
        params: dict | None = None,
        max_retries: int = 3,
    ):
        """Send a GET request and return the JSON response."""

        for attempt in range(max_retries + 1):

            self._throttle()

            response = self.session.get(
                url,
                params=params,
                timeout=30,
            )

            self.last_request_time = time.monotonic()

            if response.status_code == 200:
                return response.json()

            if response.status_code == 429:
                retry_after = response.headers.get(
                    "Retry-After"
                )

                if retry_after:
                    wait_time = float(retry_after)
                else:
                    wait_time = 2 ** attempt

                print(
                    f"SEC rate limit reached. "
                    f"Waiting {wait_time:.1f}s..."
                )

                time.sleep(wait_time)
                continue

            if response.status_code >= 500:
                wait_time = 2 ** attempt

                print(
                    f"SEC server error "
                    f"({response.status_code}). "
                    f"Retrying in {wait_time}s..."
                )

                time.sleep(wait_time)
                continue

            response.raise_for_status()

        raise RuntimeError(
            f"SEC request failed after "
            f"{max_retries + 1} attempts: {url}"
        )