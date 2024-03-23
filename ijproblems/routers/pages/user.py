from typing import Any

import psycopg
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ijproblems.internal_functions import get_internal_functions
from ijproblems.internal_functions.github_app import GITHUB_APP_CLIENT_ID
from ijproblems.internal_functions.interface import Preference
from ijproblems.routers.utils.database import get_db_conn

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get(
    "/user/{aoj_userid}/{contest_type}", response_class=HTMLResponse, name="user"
)
def get_problems(
    request: Request,
    aoj_userid: str,
    contest_type: int,
    conn: psycopg.Connection = Depends(get_db_conn),
) -> Any:
    if contest_type not in [0, 1]:
        raise HTTPException(status_code=400)
    functions = get_internal_functions(conn)
    context: dict[str, Any] = {}

    context["points"] = functions.get_points(contest_type)
    context["total_row"] = functions.get_problems_total_row(contest_type)

    context["local_ranking"] = functions.get_user_local_ranking(
        contest_type, [aoj_userid]
    )

    fixed_preference = Preference(
        ja=True,
        en=True,
        contest_type=contest_type,
        aoj_userid=aoj_userid,
        rivals=[],
        hide_solved=False,
        level_scopes=[1, 1],
    )

    user_solved_problems = functions.get_user_solved_problems(aoj_userid)
    context["user_solved_problems"] = user_solved_problems
    context["problems"] = functions.get_problems(fixed_preference, user_solved_problems)
    context["preference"] = fixed_preference
    context["level_lower"] = 1

    github_login_info = functions.get_github_login_info(request)
    context["github_login_info"] = github_login_info
    context["github_app_client_id"] = GITHUB_APP_CLIENT_ID

    if github_login_info is not None:
        context["user_likes"] = functions.get_likes(github_login_info.github_id)
    else:
        context["user_likes"] = set()

    response = templates.TemplateResponse(
        request=request,
        name="user.html",
        context=context,
    )
    return response
