from typing import Any

import psycopg
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from ijproblems.internal_functions import get_internal_functions
from ijproblems.routers.utils.database import get_db_conn

router = APIRouter()


@router.post("/api/user/like", response_class=JSONResponse, name="api_post_like")
def post_like(
    request: Request,
    aoj_id: int,
    value: int,
    conn: psycopg.Connection = Depends(get_db_conn),
) -> Any:
    functions = get_internal_functions(conn)
    github_login_info = functions.get_github_login_info(request)
    if github_login_info is None:
        raise HTTPException(status_code=401)

    github_id = github_login_info.github_id
    if value != 0:
        value = 1
    likes = functions.set_like(github_id, aoj_id, value)

    response = {"value": value, "likes": likes}
    return JSONResponse(content=response)
