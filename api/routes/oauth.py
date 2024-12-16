from fastapi import APIRouter, HTTPException
from api.models.oauth_models import GitHubCode
from api.oauth.oauth import get_github_access_token, get_github_user

router = APIRouter(
    prefix="/v1/oauth",
    tags=["oauth"],
    responses={404: {"description": "Not found"}},
)

@router.post("/github")
async def login_github(code: GitHubCode):
    try:
        access_token = await get_github_access_token(code.code)
        user_info = await get_github_user(access_token)
        print(user_info)
        return {"token": access_token}
    except HTTPException as e:
        return {"error": str(e.detail)}
