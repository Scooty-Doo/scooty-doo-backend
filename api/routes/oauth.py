"""OAuth routes"""
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends

from api.models.oauth_models import GitHubCode
from api.oauth.oauth import get_github_access_token, get_github_user
from api.db.repository_user import UserRepository as UserRepoClass
from api.models import db_models
from api.models.oauth_models import GitHubUserResponse, UserId
from api.dependencies.repository_factory import get_repository
from api.exceptions import UserNotFoundException

router = APIRouter(
    prefix="/v1/oauth",
    tags=["oauth"],
    responses={404: {"description": "Not found"}},
)

UserRepository = Annotated[
    UserRepoClass,
    Depends(get_repository(db_models.User, repository_class=UserRepoClass)),
]

@router.post("/github")
async def login_github(
    code: GitHubCode,
    user_repository: UserRepository,):
    """Login with GitHub"""
    try:
        access_token = await get_github_access_token(code.code)
        github_user_data = await get_github_user(access_token)
        github_user = GitHubUserResponse.model_validate(github_user_data)
        
        try:
            user_id = await user_repository.get_user_id_from_github_login(github_user.login)
        except UserNotFoundException:
            user = await user_repository.create_user(github_user.to_user_create())
            user_id = UserId(id=user.id)
            
        return user_id
    except HTTPException:
        raise 
