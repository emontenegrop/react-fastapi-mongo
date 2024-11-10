import pytest
from app.main import app
from fastapi import status
from httpx import ASGITransport, AsyncClient

url_api = "/api/v1/file_path"

test_uri = "https://test"


# create delete
@pytest.mark.asyncio(loop_scope="session")
async def test_post_create_delete_file_path_ok():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=test_uri
    ) as client:
        response = await client.post(
            f"{url_api}/",
            json={"path": "Repo20240813", "state": "ACTIVO", "created_by": 123},
        )
        assert response.status_code == status.HTTP_201_CREATED
        json_response = response.json()

        delete_response = await client.delete(f'{url_api}/{json_response["id"]}')
        assert delete_response.status_code == status.HTTP_201_CREATED


# create
@pytest.mark.asyncio(loop_scope="session")
async def test_post_create_file_path_ok():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=test_uri
    ) as client:
        response = await client.post(
            f"{url_api}/",
            json={"path": "local", "state": "ACTIVO", "created_by": 123},
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.json()) > 0


# get status
@pytest.mark.asyncio(loop_scope="session")
async def test_get_file_path_status_ok():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=test_uri
    ) as client:
        response = await client.get(f"{url_api}/status_active")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) > 0


# get all
@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_file_path_ok():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=test_uri
    ) as client:
        response = await client.get(f"{url_api}/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) > 0


# get by id
@pytest.mark.asyncio(loop_scope="session")
async def test_get_file_path_by_id_fault():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=test_uri
    ) as client:
        response = await client.get(f"{url_api}/01")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert len(response.json()) > 0


# update
@pytest.mark.asyncio(loop_scope="session")
async def test_put_update_file_path_ok():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=test_uri
    ) as client:
        update_response = await client.get(f"{url_api}/status_active")
        json_response = update_response.json()

        response = await client.put(
            f'{url_api}/{json_response["id"]}',
            json={"path": "local", "state": "ACTIVO", "created_by": 456},
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.json()) > 0


# update
@pytest.mark.asyncio(loop_scope="session")
async def test_put_update_file_path_fault():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=test_uri
    ) as client:

        response = await client.put(
            f"{url_api}/01",
            json={"path": "local", "state": "ACTIVO", "created_by": 456},
        )
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert len(response.json()) > 0
