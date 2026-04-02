from __future__ import annotations

from _example_support import build_offline_client


def main() -> None:
    client, transport = build_offline_client()

    transport.queue_json(
        {
            "secrets": {
                "API_KEY": {
                    "raw": "next-value",
                    "computed": "next-value",
                    "note": "rotated",
                }
            }
        }
    )
    transport.queue_json(
        {
            "name": "API_KEY",
            "value": {
                "raw": "next-value",
                "computed": "next-value",
                "note": "rotated",
            },
        }
    )

    updated = client.secrets.set("my-project", "dev", "API_KEY", "next-value")
    fetched = client.secrets.get("my-project", "dev", "API_KEY")

    print(updated.name, updated.value.raw)
    print(fetched.name, fetched.value.raw)


if __name__ == "__main__":
    main()
