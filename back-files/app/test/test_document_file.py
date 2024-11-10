import pytest
from app.main import app
from fastapi import status
from httpx import ASGITransport, AsyncClient

url_api = "/api/v1/document_file/"

url_api_path = "/api/v1/file_path"

test_uri = "https://test"

test_file = "/code/app/test/test-signed.pdf"


# create delete
@pytest.mark.asyncio(loop_scope="session")
async def test_post_create_document_file_faulth():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=test_uri
    ) as client:
        response = await client.post(
            f"{url_api}",
        )
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert len(response.json()) > 0


# create
@pytest.mark.asyncio(loop_scope="session")
async def test_post_create_delete_document_file_ok():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=test_uri
    ) as client:

        response = await client.post(
            f"{url_api}",
            data={"document": '{"file_type_id": 666,"aplication_id": "FILES", "created_by": 123,"person_id": 123}'},  # type: ignore
            files={"file": ("test.pdf", open(test_file, "rb"), "application/pdf")},
        )
        assert response.status_code == status.HTTP_200_OK
        json_response = response.json()

        delete_response = await client.delete(f'{url_api}{json_response["id"]}')
        assert delete_response.status_code == status.HTTP_200_OK


# create
@pytest.mark.asyncio(loop_scope="session")
async def test_post_create_document_file_no_path_fault():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=test_uri
    ) as client:

        update_response = await client.get(f"{url_api_path}/status_active")
        json_response = update_response.json()
        assert update_response.status_code == status.HTTP_200_OK

        update_path_response = await client.put(
            f'{url_api_path}/{json_response["id"]}',
            json={"path": "local", "state": "INACTIVO", "created_by": 456},
        )
        assert update_path_response.status_code == status.HTTP_201_CREATED

        create_response = await client.post(
            f"{url_api}",
            data={"document": '{"file_type_id": 666,"aplication_id": "FILES", "created_by": 123,"person_id": 123}'},  # type: ignore
            files={"file": ("test.pdf", open(test_file, "rb"), "application/pdf")},
        )
        assert create_response.status_code == status.HTTP_404_NOT_FOUND
        assert len(create_response.json()) > 0

        update_path_response = await client.put(
            f'{url_api_path}/{json_response["id"]}',
            json={"path": "local", "state": "ACTIVO", "created_by": 456},
        )
        assert update_path_response.status_code == status.HTTP_201_CREATED


# create
@pytest.mark.asyncio(loop_scope="session")
async def test_get_document_file_by_person_aplication_file_type_fault():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=test_uri
    ) as client:
        create_response = await client.get(f"{url_api}01/02/03")
        assert create_response.status_code == status.HTTP_404_NOT_FOUND
        assert len(create_response.json()) > 0


# get
@pytest.mark.asyncio(loop_scope="session")
async def test_get_document_file_by_person_aplication_file_type_ok():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=test_uri
    ) as client:

        response = await client.post(
            f"{url_api}",
            data={"document": '{"file_type_id": 666,"aplication_id": "FILES", "created_by": 123,"person_id": 123}'},  # type: ignore
            files={"file": ("test.pdf", open(test_file, "rb"), "application/pdf")},
        )
        assert response.status_code == status.HTTP_200_OK
        json_response = response.json()

        find_response = await client.get(
            f'{url_api}{json_response["person_id"]}/{json_response["aplication_id"]}/{json_response["file_type_id"]}'
        )
        assert find_response.status_code == status.HTTP_200_OK
        assert len(find_response.json()) > 0

        delete_response = await client.delete(f'{url_api}{json_response["id"]}')
        assert delete_response.status_code == status.HTTP_200_OK


# get
@pytest.mark.asyncio(loop_scope="session")
async def test_get_document_file_by_id_ok():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=test_uri
    ) as client:

        response = await client.post(
            f"{url_api}",
            data={"document": '{"file_type_id": 666,"aplication_id": "FILES", "created_by": 123,"person_id": 123}'},  # type: ignore
            files={"file": ("test.pdf", open(test_file, "rb"), "application/pdf")},
        )
        assert response.status_code == status.HTTP_200_OK
        json_response = response.json()

        find_response = await client.get(f'{url_api}{json_response["id"]}')
        assert find_response.status_code == status.HTTP_200_OK

        delete_response = await client.delete(f'{url_api}{json_response["id"]}')
        assert delete_response.status_code == status.HTTP_200_OK


# get
@pytest.mark.asyncio(loop_scope="session")
async def test_get_document_file_by_id_fault():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=test_uri
    ) as client:

        find_response = await client.get(f"{url_api}672a8eb9143123771720e519")
        assert find_response.status_code == status.HTTP_404_NOT_FOUND


# put
@pytest.mark.asyncio(loop_scope="session")
async def test_put_update_delete_document_file_ok():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=test_uri
    ) as client:

        response = await client.post(
            f"{url_api}",
            data={"document": '{"file_type_id": 666,"aplication_id": "FILES", "created_by": 123,"person_id": 123}'},  # type: ignore
            files={"file": ("test.pdf", open(test_file, "rb"), "application/pdf")},
        )
        assert response.status_code == status.HTTP_200_OK
        json_response = response.json()

        update_response = await client.put(
            f'{url_api}{json_response["id"]}', json={"block": False}
        )
        assert update_response.status_code == status.HTTP_200_OK

        delete_response = await client.delete(f'{url_api}{json_response["id"]}')
        assert delete_response.status_code == status.HTTP_200_OK


# put
@pytest.mark.asyncio(loop_scope="session")
async def test_put_update_delete_document_file_fault():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=test_uri
    ) as client:

        update_response = await client.put(
            f"{url_api}64371d2322b746ef647f7b4f", json={"block": False}
        )
        assert update_response.status_code == status.HTTP_404_NOT_FOUND


# get
@pytest.mark.asyncio(loop_scope="session")
async def test_get_document_file_data_by_id_ok():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=test_uri
    ) as client:

        response = await client.post(
            f"{url_api}",
            data={"document": '{"file_type_id": 666,"aplication_id": "FILES", "created_by": 789,"person_id": 123}'},  # type: ignore
            files={"file": ("test.pdf", open(test_file, "rb"), "application/pdf")},
        )
        assert response.status_code == status.HTTP_200_OK
        json_response = response.json()

        find_response = await client.get(f'{url_api}data/{json_response["id"]}')
        assert find_response.status_code == status.HTTP_200_OK

        delete_response = await client.delete(f'{url_api}{json_response["id"]}')
        assert delete_response.status_code == status.HTTP_200_OK


# get
@pytest.mark.asyncio(loop_scope="session")
async def test_get_document_file_person_id_aplication_id_ok():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=test_uri
    ) as client:

        response = await client.post(
            f"{url_api}",
            data={"document": '{"file_type_id": 666,"aplication_id": "FILES", "created_by": 789,"person_id": 123}'},  # type: ignore
            files={"file": ("test.pdf", open(test_file, "rb"), "application/pdf")},
        )
        assert response.status_code == status.HTTP_200_OK
        json_response = response.json()

        find_response = await client.get(
            f'{url_api}{json_response["person_id"]}/{json_response["aplication_id"]}'
        )
        assert find_response.status_code == status.HTTP_200_OK

        delete_response = await client.delete(f'{url_api}{json_response["id"]}')
        assert delete_response.status_code == status.HTTP_200_OK


# create
@pytest.mark.asyncio(loop_scope="session")
async def test_post_create_delete_document_file_signed_validate_ok():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=test_uri
    ) as client:

        response = await client.post(
            f"{url_api}signed_validate/",
            data={
                "document": '{"file_type_id": 666,"aplication_id": "FILES", "created_by": 123,"person_id": 123}',
                "cedula_ruc": "0604139030",
            },  # type: ignore
            files={
                "file": (
                    "test-signed.pdf",
                    open("/code/app/test/test-signed.pdf", "rb"),
                    "application/pdf",
                )
            },
        )

        assert response.status_code == status.HTTP_200_OK
        json_response = response.json()

        delete_response = await client.delete(f'{url_api}{json_response["id"]}')
        assert delete_response.status_code == status.HTTP_200_OK


# create
@pytest.mark.asyncio(loop_scope="session")
async def test_post_create_delete_document_file_signed_validate_fault():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=test_uri
    ) as client:

        response = await client.post(
            f"{url_api}signed_validate/",
            data={
                "document": '{"file_type_id": 666,"aplication_id": "FILES", "created_by": 123,"person_id": 123}',
                "cedula_ruc": "1715376352",
            },  # type: ignore
            files={
                "file": (
                    "test-signed.pdf",
                    open("/code/app/test/test-signed.pdf", "rb"),
                    "application/pdf",
                )
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        json_response = response.json()
