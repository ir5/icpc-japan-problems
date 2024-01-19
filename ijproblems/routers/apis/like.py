import os
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

if os.environ.get("USE_MOCK"):
    from ijproblems.mock_functions.mock import (
        MockInternalFunctions as InternalFunctions,
    )


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.post("/api/user/like", response_class=JSONResponse, name="api_post_like")
def post_like(request: Request, aoj_id: int, value: int) -> Any:
    functions = InternalFunctions()
    github_login_info = functions.get_github_login_info(request)
    if github_login_info is None:
        raise HTTPException(status_code=401)

    github_id = github_login_info.github_id
    if value != 0:
        value = 1
    likes = functions.set_like(github_id, aoj_id, value)

    response = {"value": value, "likes": likes}
    return JSONResponse(content=response)
