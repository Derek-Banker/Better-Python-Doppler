from __future__ import annotations

import _example_support  # noqa: F401

from better_python_doppler import Doppler


def main() -> None:
    client = Doppler(service_token="dp.st.example-token")

    print(client.service_token)
    print(client.Secrets is client.secrets)


if __name__ == "__main__":
    main()
