"""Tests for the health check endpoint."""


def test_health_check_returns_ok(client) -> None:
    """Health endpoint should return 200 with status ok."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
