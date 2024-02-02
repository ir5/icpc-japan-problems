from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ijproblems.internal_functions.github_app_client_id import GITHUB_APP_CLIENT_ID
from ijproblems.internal_functions import InternalFunctions
from ijproblems.routers.utils.cookie import get_preference_from_cookie

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/problem/{aoj_id}", response_class=HTMLResponse, name="statistics")
def get_problems(
    request: Request,
    aoj_id: int,
) -> Any:
    functions = InternalFunctions()
    context: dict[str, Any] = {}

    problem = functions.get_problem(aoj_id)
    if problem is None:
        raise HTTPException(status_code=400)
    context["problem"] = problem
    context["points"] = functions.get_points(problem.contest_type)
    context["problem_solved_user_count"] = functions.get_solved_user_count(aoj_id)

    if problem.contest_type == 0:
        if problem.org == "Official":
            contest = "ICPC Japan Domestic Contest"
        elif problem.org == "JAG":
            jag_contest_name = "Contest"
            if len(problem.used_in) > 0:
                jag_contest_name += f" {problem.used_in}"
            contest = f"JAG Practice {jag_contest_name} for Japan Domestic"
    elif problem.contest_type == 1:
        if problem.org == "Official":
            contest = "ICPC Asia Japan Regional Contest"
        elif problem.org == "JAG":
            contest = f"JAG {problem.used_in} Contest"
    context["contest"] = contest

    github_login_info = functions.get_github_login_info(request)
    context["github_login_info"] = github_login_info
    context["github_app_client_id"] = GITHUB_APP_CLIENT_ID

    if github_login_info is not None:
        context["user_likes"] = functions.get_likes(github_login_info.github_id)
    else:
        context["user_likes"] = set()

    preference = get_preference_from_cookie(request)
    context["preference"] = preference
    user_solved_problems = functions.get_user_solved_problems(preference.aoj_userid)
    context["user_solved_problems"] = user_solved_problems

    response = templates.TemplateResponse(
        request=request,
        name="statistics.html",
        context=context,
    )
    return response
