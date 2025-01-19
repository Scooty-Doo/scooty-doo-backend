"""Module for testing oauth services module"""

from unittest.mock import patch

import pytest
from fastapi import HTTPException
from fastapi.security.oauth2 import SecurityScopes

from api.services.oauth import get_github_access_token, httpx, security_check, settings, get_github_user


class TestOauth:
    """Class to test oauth services functionality"""

    def test_security_check(self, monkeypatch):
        """Tests security check"""
        monkeypatch.setattr(settings, "jwt_secret", "testysecrets")

        res = security_check(
            SecurityScopes(["user", "admin"]),
            token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjUxMjUiLCJzY29wZXMiOlsidXNlciIsImFkbWluIl19.IUomA__M_ua7NT75aPSzHkVnTwzFv_Otw5mfxFNQyeY",
        )
        assert res == 125125

    def test_security_check_no_scopes(self, monkeypatch):
        """Tests security with no scopes"""
        monkeypatch.setattr(settings, "jwt_secret", "testysecrets")

        res = security_check(
            SecurityScopes(),
            token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjUxMjUiLCJzY29wZXMiOlsidXNlciIsImFkbWluIl19.IUomA__M_ua7NT75aPSzHkVnTwzFv_Otw5mfxFNQyeY",
        )
        assert res == 125125

    def test_security_check_invalid_token(self, monkeypatch):
        """Tests security fail with invalid token"""
        monkeypatch.setattr(settings, "jwt_secret", "testysecrets")

        with pytest.raises(HTTPException):
            security_check(SecurityScopes(["user", "admin"]), token={1})

    def test_security_check_no_user(self, monkeypatch):
        """Tests security fail with no sub in token"""
        monkeypatch.setattr(settings, "jwt_secret", "testysecrets")

        with pytest.raises(HTTPException):
            security_check(
                SecurityScopes(["user", "admin"]),
                token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGEiOiIxMjUxMjUiLCJzY29wZXMiOlsidXNlciIsImFkbWluIl19.nQABBB7bmVjgx0uRZNE7w-sq51BIGZrkIb8gT_56des",
            )

    def test_security_check_wrong_scopes(self, monkeypatch):
        """Tests security fail with wrong scopes"""
        monkeypatch.setattr(settings, "jwt_secret", "testysecrets")

        with pytest.raises(HTTPException):
            security_check(
                SecurityScopes(["apa"]),
                token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjUxMjUiLCJzY29wZXMiOlsidXNlciIsImFkbWluIl19.IUomA__M_ua7NT75aPSzHkVnTwzFv_Otw5mfxFNQyeY",
            )

    @pytest.mark.asyncio
    @patch(
        "api.services.oauth.httpx.AsyncClient.post",
        return_value=httpx.Response(200, json={"access_token": "pjasc890123"}),
    )
    async def test_get_github_access_token(self, monkeypatch):
        """Tests gitub action token fetcher"""
        await get_github_access_token("awdiophawpiod")
        monkeypatch.assert_called_once()
        monkeypatch.assert_called_with(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": "awdiophawpiod",
                "redirect_uri": settings.github_redirect_uri,
            },
        )

    @pytest.mark.asyncio
    @patch(
        "api.services.oauth.httpx.AsyncClient.post",
        return_value=httpx.Response(400, json={"ape": "Apan-Papansson"}),
    )
    async def test_get_github_access_bad_response(self, monkeypatch):
        """Tests gitub action user fetcher"""
        with pytest.raises(HTTPException) as error:
            await get_github_access_token("awdiophawpiod")
            monkeypatch.assert_called_once()
            monkeypatch.assert_called_with(
                "https://github.com/login/oauth/access_token",
                headers={"Authorization": "Bearer pjasc890123"},
            )


    @pytest.mark.asyncio
    @patch(
        "api.services.oauth.httpx.AsyncClient.get",
        return_value=httpx.Response(200, json={"access_token": "Apan-Papansson"}),
    )
    async def test_get_github_user(self, monkeypatch):
        """Tests gitub action user fetcher"""
        await get_github_user("pjasc890123")
        monkeypatch.assert_called_once()
        monkeypatch.assert_called_with(
            "https://api.github.com/user",
            headers={"Authorization": "Bearer pjasc890123"},
        )

    @pytest.mark.asyncio
    @patch(
        "api.services.oauth.httpx.AsyncClient.get",
        return_value=httpx.Response(200, json={"ape": "Apan-Papansson"}),
    )
    async def test_get_github_user_no_token(self, monkeypatch):
        """Tests gitub action user fetcher"""
        with pytest.raises(HTTPException) as error:
            await get_github_access_token("pjasc890123")
            monkeypatch.assert_called_once()
            monkeypatch.assert_called_with(
                "https://api.github.com/user",
                headers={"Authorization": "Bearer pjasc890123"},
            )

    @pytest.mark.asyncio
    @patch(
        "api.services.oauth.httpx.AsyncClient.get",
        return_value=httpx.Response(400, json={"access_token": "Apan-Papansson"}),
    )
    async def test_get_github_user_fail(self, monkeypatch):
        """Tests gitub action user fetcher"""
        with pytest.raises(HTTPException) as error:
            res = await get_github_user("pjasc890123")
            print(res)
            monkeypatch.assert_called_once()
            monkeypatch.assert_called_with(
                "https://api.github.com/user",
                headers={"Authorization": "Bearer pjasc890123"},
            )
