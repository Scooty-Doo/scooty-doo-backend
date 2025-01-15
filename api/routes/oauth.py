"""OAuth routes"""

from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException

from api.config import settings
from api.db.repository_admin import AdminRepository as AdminRepoClass
from api.db.repository_user import UserRepository as UserRepoClass
from api.dependencies.repository_factory import get_repository
from api.exceptions import UserNotFoundException
from api.models import db_models
from api.models.oauth_models import GitHubRequest, GitHubUserResponse
from api.services.oauth import get_github_access_token, get_github_user, get_id

router = APIRouter(
    prefix="/v1/oauth",
    tags=["oauth"],
    responses={404: {"description": "Not found"}},
)

UserRepository = Annotated[
    UserRepoClass,
    Depends(get_repository(db_models.User, repository_class=UserRepoClass)),
]

AdminRepository = Annotated[
    AdminRepoClass,
    Depends(get_repository(db_models.Admin, repository_class=AdminRepoClass)),
]


@router.post("/github")
async def login_github(
    request: GitHubRequest, admin_repository: AdminRepository, user_repository: UserRepository
):
    """Login with GitHub"""
    try:
        access_token = await get_github_access_token(request.code)
        github_user_data = await get_github_user(access_token)
        github_user = GitHubUserResponse.model_validate(github_user_data)
        try:
            user_id, scopes = await get_id(
                github_user, request.role, admin_repository, user_repository
            )
        except UserNotFoundException as e:
            raise HTTPException(status_code=404, detail="Admin not found") from e
        token = jwt.encode(
            {"sub": str(user_id.id), "scopes": scopes}, settings.jwt_secret, algorithm="HS256"
        )
        return {"access_token": token, "token_type": "bearer"}
    except HTTPException as e:
        raise e
