from pydantic import BaseModel

class GitHubCode(BaseModel):
    code: str
