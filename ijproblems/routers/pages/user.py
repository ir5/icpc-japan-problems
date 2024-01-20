from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ijproblems.internal_functions import InternalFunctions
from ijproblems.routers.utils.cookie import get_preference_from_cookie
from ijproblems.internal_functions.interface import Preference

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/user/{aoj_userid}/{contest_type}", response_class=HTMLResponse, name="user")
def get_problems(
    request: Request,
    aoj_userid: str,
    contest_type: int
) -> Any:
    functions = InternalFunctions()
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
