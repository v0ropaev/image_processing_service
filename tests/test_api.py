import pytest
import httpx
from io import BytesIO
from uuid import uuid4


async def register_user(async_client: httpx.AsyncClient) -> dict[str, str]:
    random_uuid = uuid4()
    response = await async_client.post(
        "/registration",
        json={"email": f"{random_uuid}testuser@example.com", "password": "password"}
    )
    assert response.status_code == 200
    token = response.json().get("access_token")
    return {"token": token, "login": f"{random_uuid}testuser@example.com"}


@pytest.mark.asyncio
async def test_registration(async_client: httpx.AsyncClient):
    registration_info = await register_user(async_client)
    auth_token = registration_info["token"]
    assert auth_token is not None


@pytest.mark.asyncio
async def test_login(async_client: httpx.AsyncClient):
    registration_info = await register_user(async_client)
    user_login = registration_info["login"]
    auth_token = registration_info["token"]

    response = await async_client.post(
        "/login",
        data={"username": user_login, "password": "password"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_upload_images(async_client: httpx.AsyncClient):
    registration_info = await register_user(async_client)
    auth_token = registration_info["token"]

    image_bytes = BytesIO(b"fake image data")
    image_bytes.name = "test.jpg"
    response = await async_client.post(
        "/upload",
        files={"files": ("test.jpg", image_bytes, "image/jpeg")},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data.get("task_id") is not None


@pytest.mark.asyncio
async def test_get_status(async_client: httpx.AsyncClient):
    registration_info = await register_user(async_client)
    user_login = registration_info["login"]
    auth_token = registration_info["token"]

    image_bytes = BytesIO(b"fake image data")
    image_bytes.name = "test.jpg"
    upload_response = await async_client.post(
        "/upload",
        files={"files": ("test.jpg", image_bytes, "image/jpeg")},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert upload_response.status_code == 200
    task_id = upload_response.json().get("task_id")
    assert task_id is not None

    status_response = await async_client.get(
        f"/status/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert status_response.status_code == 200
    task_status = status_response.json().get("task_status")
    assert task_status is not None


@pytest.mark.asyncio
async def test_get_my_id(async_client: httpx.AsyncClient):
    registration_info = await register_user(async_client)
    user_login = registration_info["login"]
    auth_token = registration_info["token"]

    response = await async_client.get(
        "/get_my_id",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    your_id = response.json().get("your_id")
    assert your_id is not None


@pytest.mark.asyncio
async def test_get_history(async_client: httpx.AsyncClient):
    registration_info = await register_user(async_client)
    auth_token = registration_info["token"]

    image_bytes = BytesIO(b"fake image data")
    image_bytes.name = "test.jpg"
    upload_response = await async_client.post(
        "/upload",
        files={"files": ("test.jpg", image_bytes, "image/jpeg")},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert upload_response.status_code == 200
    task_id = upload_response.json().get("task_id")
    assert task_id is not None

    status_response = await async_client.get(
        f"/status/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert status_response.status_code == 200
    task_status = status_response.json().get("task_status")
    assert task_status is not None


@pytest.mark.asyncio
async def test_download_task_images(async_client: httpx.AsyncClient):
    registration_info = await register_user(async_client)
    auth_token = registration_info["token"]

    image_bytes = BytesIO(b"fake image data")
    image_bytes.name = "test.jpg"
    upload_response = await async_client.post(
        "/upload",
        files={"files": ("test.jpg", image_bytes, "image/jpeg")},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert upload_response.status_code == 200
    task_id = upload_response.json().get("task_id")
    assert task_id is not None

    download_response = await async_client.get(
        f"/task/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert download_response.headers["Content-Type"] == "application/zip"
    assert "Content-Disposition" in download_response.headers
    assert download_response.headers["Content-Disposition"] == f"attachment; filename={task_id}.zip"
