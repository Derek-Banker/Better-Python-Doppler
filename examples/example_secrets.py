from __future__ import annotations

from _example_support import build_offline_client


def main() -> None:
    client, transport = build_offline_client()

    transport.queue_json({"names": ["API_KEY", "TIMEOUT"]})
    transport.queue_json(
        {
            "secrets": {
                "API_KEY": {
                    "raw": "alpha",
                    "computed": "alpha",
                    "note": "primary",
                },
                "TIMEOUT": {
                    "raw": "30",
                    "computed": "30",
                    "note": None,
                },
            }
        }
    )

    names = client.Secrets.list_names("my-project", "dev")
    values = client.secrets.as_dict("my-project", "dev")

    print(f"Compatibility alias works: {client.Secrets is client.secrets}")
    print(names)
    print(values)


if __name__ == "__main__":
    main()
