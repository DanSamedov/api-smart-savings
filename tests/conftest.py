import pytest
from unittest.mock import MagicMock, patch

# Patch SQLAlchemy create_engine globally for all tests
@pytest.fixture(autouse=True, scope="session")
def patch_create_engine():
    with patch("app.db.session.create_engine", return_value=MagicMock()):
        yield

# Patch get_session globally
@pytest.fixture(autouse=True)
def patch_get_session():
    from app.api import dependencies
    dependencies.get_session = lambda: iter([])
