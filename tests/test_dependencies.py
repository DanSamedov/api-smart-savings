import pytest
from fastapi import HTTPException
from fastapi.security import HTTPBasicCredentials

import app.api.dependencies as auth_module


@pytest.fixture(autouse=True)
def patch_auth_constants(monkeypatch):
    """Default to valid credentials for most tests."""

    monkeypatch.setattr(auth_module, "USERNAME", "admin")
    monkeypatch.setattr(auth_module, "PASSWORD", "secret")


def make_credentials(username: str, password: str):
    """Helper to create HTTPBasicCredentials."""

    return HTTPBasicCredentials(username=username, password=password)


def test_authenticate_valid_credentials():
    """Should return True when username and password match."""

    creds = make_credentials("admin", "secret")
    result = auth_module.authenticate(creds)
    assert result is True


@pytest.mark.parametrize(
    "username,password",
    [
        ("wrong", "secret"),
        ("admin", "wrong"),
    ],
)
def test_authenticate_invalid_credentials(username, password):
    """Should raise 401 when username or password is wrong."""

    creds = make_credentials(username, password)
    with pytest.raises(HTTPException) as exc:
        auth_module.authenticate(creds)

    assert exc.value.status_code == 401
    assert "Invalid credentials" in exc.value.detail


def test_authenticate_missing_config(monkeypatch):
    """Should raise 500 when USERNAME or PASSWORD is None."""

    monkeypatch.setattr(auth_module, "USERNAME", None)
    monkeypatch.setattr(auth_module, "PASSWORD", None)

    creds = make_credentials("admin", "secret")
    with pytest.raises(HTTPException) as exc:
        auth_module.authenticate(creds)

    assert exc.value.status_code == 500
    assert "Configuration error" in exc.value.detail
