"""Tests for JWT-protected authentication endpoints."""

from unittest.mock import AsyncMock, patch


def test_me_without_token_returns_401(client) -> None:
    """Protected endpoint should reject requests without a bearer token."""
    response = client.get("/api/v1/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_me_with_malformed_token_returns_401(client) -> None:
    """Protected endpoint should reject malformed bearer tokens."""
    with patch(
        "app.dependencies.auth._fetch_jwks",
        new_callable=AsyncMock,
        return_value={"keys": []},
    ):
        response = client.get(
            "/api/v1/me",
            headers={"Authorization": "Bearer not-a-valid-jwt"},
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


def test_me_with_valid_token_returns_user_claims(client, mock_verify_token) -> None:
    """Protected endpoint should return user claims for a valid token."""
    response = client.get(
        "/api/v1/me",
        headers={"Authorization": "Bearer valid.jwt.token"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": "user-123",
        "email": "user@example.com",
        "role": "authenticated",
    }
    mock_verify_token.assert_awaited_once()
