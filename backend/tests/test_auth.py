import asyncio
import os

import httpx
import pytest

from app.db.sqlite import get_connection
from app.main import app

TEST_PASSWORD = os.environ["TEST_PASSWORD"]
TEST_WRONG_PASSWORD = os.environ["TEST_WRONG_PASSWORD"]


@pytest.fixture(autouse=True)
def clean_users() -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM users")
        connection.commit()


def test_registration_login_me_and_nickname_update() -> None:
    async def scenario() -> None:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            register = await client.post(
                "/api/auth/register",
                json={"email": "student@example.com", "password": TEST_PASSWORD, "nickname": "공부왕"},
            )
            assert register.status_code == 201
            assert register.json()["nickname"] == "공부왕"
            assert "password" not in register.text

            login = await client.post(
                "/api/auth/login",
                json={"email": "student@example.com", "password": TEST_PASSWORD},
            )
            assert login.status_code == 200
            assert "buildlog_session" in client.cookies

            me = await client.get("/api/auth/me")
            assert me.status_code == 200
            assert me.json()["email"] == "student@example.com"

            nickname = await client.patch("/api/auth/me/nickname", json={"nickname": "새공부왕"})
            assert nickname.status_code == 200
            assert nickname.json()["nickname"] == "새공부왕"

    asyncio.run(scenario())


def test_auth_validation_and_permissions() -> None:
    async def scenario() -> None:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            short_password = await client.post(
                "/api/auth/register",
                json={"email": "student@example.com", "password": "short", "nickname": "공부왕"},
            )
            assert short_password.status_code == 422

            register = await client.post(
                "/api/auth/register",
                json={"email": "student@example.com", "password": TEST_PASSWORD, "nickname": "공부왕"},
            )
            assert register.status_code == 201

            duplicate = await client.post(
                "/api/auth/register",
                json={"email": "student@example.com", "password": TEST_PASSWORD, "nickname": "다른닉"},
            )
            assert duplicate.status_code == 409

            wrong_login = await client.post(
                "/api/auth/login",
                json={"email": "student@example.com", "password": TEST_WRONG_PASSWORD},
            )
            assert wrong_login.status_code == 401

            no_session = httpx.AsyncClient(transport=transport, base_url="http://testserver")
            async with no_session:
                unauthorized = await no_session.get("/api/auth/me")
                assert unauthorized.status_code == 401

    asyncio.run(scenario())
