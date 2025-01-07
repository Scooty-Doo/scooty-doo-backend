"""Module for Oauth"""

import os

import httpx
from typing import Annotated, Union
from dotenv import load_dotenv
from fastapi import HTTPException, Depends
from api.models import db_models
from api.models.oauth_models import UserId, GitHubUserResponse
from api.exceptions import UserNotFoundException
from api.dependencies.repository_factory import get_repository


load_dotenv()


async def get_github_access_token(code: str):
    """Get the access token from the GitHub API."""
    url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    data = {
        "client_id": os.getenv("GITHUB_CLIENT_ID"),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
        "code": code,
        "redirect_uri": os.getenv("GITHUB_REDIRECT_URI"),
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

async def get_id(github_user: GitHubUserResponse, role: str, admin_repository, user_repository) -> UserId:
    """Gets the id of the user or admin from the github_login.
    
    If the user isn't in the database it is created.
    If the admin isn't in the database a UserNotFoundException is raised.
    """
    if role == "admin":
        try:
            user_id = await admin_repository.get_admin_id_from_github_login(github_user.login)
            user_id = UserId(id=user_id)
            return user_id
        except UserNotFoundException:
            raise UserNotFoundException
    try:
        user_id = await user_repository.get_user_id_from_github_login(github_user.login)
        user_id = UserId(id=user_id)
    except UserNotFoundException:
        if role == "admin":
            raise UserNotFoundException
        user_create = github_user.to_user_create()
        user = await user_repository.create_user(user_create.model_dump())
        user_id = UserId(id=user.id)
    return user_id
