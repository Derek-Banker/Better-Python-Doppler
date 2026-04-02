from __future__ import annotations

import os

import _example_support  # noqa: F401

from better_python_doppler import Doppler


def main() -> None:
    os.environ["DOPPLER_SERVICE_TOKEN"] = "dp.st.env-token"

    client = Doppler(service_token_environ_name="DOPPLER_SERVICE_TOKEN")

    print(client.service_token)


if __name__ == "__main__":
    main()
