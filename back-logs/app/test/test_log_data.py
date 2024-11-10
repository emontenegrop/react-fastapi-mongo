import pytest
from app.main import app
from fastapi import status
from httpx import ASGITransport, AsyncClient

url_api = "/api/v1/log_data/"

test_uri = "https://test"


body = {
    "timestamp": "04/01/2024 09:17:49",
    "application_code": "aplicacion",
    "status": "failure / success",
    "event_id": "2213812294562653681",
    "error": {"status_code": 402, "description": "ERROR:"},
    "actor": {"user_name": "user", "client": "apifiles", "api_path": "/root"},
}


# POST
@pytest.mark.asyncio(loop_scope="session")
async def test_post_create_log_data_ok():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=test_uri
    ) as client:
        response = await client.post(url_api, json=body)
        assert response.status_code == status.HTTP_200_OK



# POST
@pytest.mark.asyncio(loop_scope="session")
async def test_get_log_data_ok():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=test_uri
    ) as client:            
        find_response = await client.get(f"{url_api}2213812294562653681")       
        assert find_response.status_code == status.HTTP_200_OK