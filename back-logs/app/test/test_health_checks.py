import pytest
from app.main import app
from fastapi import status
from httpx import ASGITransport, AsyncClient

url_api = "/api/v1/health/"

test_uri = "https://test"


# create
@pytest.mark.asyncio(loop_scope="session")
async def test_get_health_checks_ok():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=test_uri
    ) as client:
        response = await client.get(f"{url_api}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) > 0
