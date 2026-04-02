from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import _example_support  # noqa: F401

from better_python_doppler import Doppler


def main() -> None:
    with TemporaryDirectory() as temp_dir:
        dotenv_path = Path(temp_dir) / ".env.example"
        dotenv_path.write_text(
            "DOPPLER_SERVICE_TOKEN=dp.st.dotenv-token\n",
            encoding="utf-8",
        )

        client = Doppler.from_env(
            "DOPPLER_SERVICE_TOKEN",
            dotenv_path=dotenv_path,
            override=True,
        )

    print(client.service_token)


if __name__ == "__main__":
    main()
