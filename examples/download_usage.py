from __future__ import annotations

from _example_support import build_offline_client


def main() -> None:
    client, transport = build_offline_client()

    transport.queue_json({"API_KEY": "alpha", "TIMEOUT": "30"})
    transport.queue_text("API_KEY=alpha\nTIMEOUT=30\n")

    as_json = client.secrets.download("my-project", "dev", format="json")
    as_env = client.secrets.download(
        "my-project",
        "dev",
        format="env",
        secrets=["API_KEY", "TIMEOUT"],
    )

    print(as_json)
    print(as_env)


if __name__ == "__main__":
    main()
