"""Module for Oauth"""

from typing import Annotated

import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2AuthorizationCodeBearer, SecurityScopes
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from api.config import settings
from api.db.repository_user import UserRepository as UserRepoClass
from api.dependencies.repository_factory import get_repository
from api.exceptions import UserNotFoundException
from api.models import db_models
from api.models.oauth_models import GitHubUserResponse, TokenData, UserId

UserRepository = Annotated[
    UserRepoClass,
    Depends(get_repository(db_models.User, repository_class=UserRepoClass)),
]

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://github.com/login/oauth/authorize",
    tokenUrl="https://github.com/login/oauth/access_token",
    scopes={"user": "Rent bikes, see own data", "admin": "Full access"},
)


async def get_github_access_token(code: str):
    """Get the access token from the GitHub API."""
    url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    data = {
        "client_id": settings.github_client_id,
        "client_secret": settings.github_client_secret,
        "code": code,
        "redirect_uri": settings.github_redirect_uri,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch access token")

    token_data = response.json()
    access_token = token_data.get("access_token")

    if not access_token:
        raise HTTPException(status_code=400, detail="Access token not found")

    return access_token


async def get_github_user(access_token: str):
    """Get the user details from the GitHub API."""
    url = "https://api.github.com/user"
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch user info")

    return response.json()


async def get_id(github_user: GitHubUserResponse, role: str, admin_repository, user_repository):
    """Gets the id of the user or admin from the github_login database field.

    If the user isn't in the database it is created.
    If the admin isn't in the database a UserNotFoundException is raised.
    """
    if role == "admin":
        try:
            user_id = await admin_repository.get_admin_id_from_github_login(github_user.login)
            user_id = UserId(id=user_id)
            return user_id, ["admin"]
        except UserNotFoundException as e:
            raise HTTPException(status_code=404, detail="Admin not found") from e
    try:
        user_id = await user_repository.get_user_id_from_github_login(github_user.login)
        user_id = UserId(id=user_id)
    except UserNotFoundException:
        user_create = github_user.to_user_create()
        user = await user_repository.create_user(user_create.model_dump())
        user_id = UserId(id=user.id)
    return user_id, ["user"]


def security_check(
    security_scopes: SecurityScopes,
    token=Depends(oauth2_scheme),
) -> int:
    """Checks a token for user id and scopes, returns user/admin ID"""
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(user_id=user_id, scopes=token_scopes)
    except (InvalidTokenError, ValidationError) as e:
        raise credentials_exception from e
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return int(token_data.user_id)
