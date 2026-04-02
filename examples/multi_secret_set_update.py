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
                    "note": None,
                },
                "TIMEOUT": {
                    "raw": "30",
                    "computed": "30",
                    "note": None,
                },
            }
        }
    )
    transport.queue_json(
        {
            "secrets": {
                "API_KEY": {
                    "raw": "rotated-value",
                    "computed": "rotated-value",
                    "note": None,
                },
                "TIMEOUT": {
                    "raw": "60",
                    "computed": "60",
                    "note": None,
                },
            }
        }
    )

    updated = client.secrets.set_many(
        "my-project",
        "dev",
        {
            "API_KEY": "next-value",
            "TIMEOUT": "30",
        },
    )
    compatibility_update = client.Secrets.update(
        "my-project",
        "dev",
        secrets={
            "API_KEY": "rotated-value",
            "TIMEOUT": "60",
        },
    )

    print([(secret.name, secret.value.raw) for secret in updated])
    print([(secret.name, secret.value.raw) for secret in compatibility_update])


if __name__ == "__main__":
    main()
