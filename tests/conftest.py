from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from focusrelay_api.config import settings
from focusrelay_api.main import app

TEST_TOKEN = "test-secret-token"


@pytest.fixture(autouse=True)
def _enable_auth():
    """Enable auth for all tests by default."""
    original = settings.api_token
    settings.api_token = TEST_TOKEN
    yield
    settings.api_token = original


@pytest.fixture
def client():
    return TestClient(app, headers={"Authorization": f"Bearer {TEST_TOKEN}"})


@pytest.fixture
def unauthed_client():
    return TestClient(app)


@pytest.fixture
def mock_cli():
    """Patch run_focusrelay to return canned responses without calling the real CLI."""
    with patch("focusrelay_api.main.run_focusrelay", new_callable=AsyncMock) as mock:
        yield mock
