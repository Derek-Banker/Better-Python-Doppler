from __future__ import annotations

from unittest.mock import Mock

from better_python_doppler.transport import RequestsTransport


def test_requests_transport_builds_full_url_auth_header_and_default_timeout() -> None:
    response = Mock()
    session = Mock()
    session.request.return_value = response

    transport = RequestsTransport("dp.st.test-token", session=session)

    result = transport.get(
        "/v3/configs/config/secrets",
        params={"project": "proj", "config": "dev"},
        headers={"Accept": "application/json"},
    )

    assert result is response
    session.request.assert_called_once_with(
        method="GET",
        url="https://api.doppler.com/v3/configs/config/secrets",
        params={"project": "proj", "config": "dev"},
        json=None,
        headers={
            "Accept": "application/json",
            "Authorization": "Bearer dp.st.test-token",
        },
        timeout=10.0,
    )
    response.raise_for_status.assert_called_once_with()


def test_requests_transport_honors_custom_base_url_timeout_and_json_payload() -> None:
    response = Mock()
    session = Mock()
    session.request.return_value = response

    transport = RequestsTransport(
        "dp.st.test-token",
        base_url="https://custom.example/",
        timeout=5.0,
        session=session,
    )

    result = transport.post(
        "v3/configs/config/secrets",
        json={"project": "proj", "config": "dev", "secrets": {"API_KEY": "alpha"}},
        headers={"accept": "application/json", "content-type": "application/json"},
        timeout=2.5,
    )

    assert result is response
    session.request.assert_called_once_with(
        method="POST",
        url="https://custom.example/v3/configs/config/secrets",
        params=None,
        json={"project": "proj", "config": "dev", "secrets": {"API_KEY": "alpha"}},
        headers={
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": "Bearer dp.st.test-token",
        },
        timeout=2.5,
    )
    response.raise_for_status.assert_called_once_with()
