"""Module for testing transaction routes"""

from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from api.db.repository_transaction import TransactionRepository
from api.main import app
from api.routes.me import security_check
from tests.mock_files.objects import fake_transactions_data
from tests.utils import get_fake_json_data


class TestTransactions:
    """Class to transaction route functionality"""

    async def mock_security_check(self, _: str = "", required_scopes: list = None):
        """Mocks security check for transaction routes"""
        return {"user_id": 1, "scopes": required_scopes}

    @pytest.mark.asyncio
    async def test_get_transactions(self, monkeypatch):
        """Tests get transactions route"""

        app.dependency_overrides[security_check] = self.mock_security_check

        mock_transaction = AsyncMock(return_value=fake_transactions_data)
        monkeypatch.setattr(TransactionRepository, "get_transactions", mock_transaction)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://localhost:8000/"
        ) as ac:
            response = await ac.get("v1/transactions/")

        assert response.status_code == 200
        assert response.json() == get_fake_json_data("transactions")
