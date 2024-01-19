import datetime
import json
import os
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ijproblems.internal_functions_interface import Preference

if os.environ.get("USE_MOCK"):
    from ijproblems.mock_functions.mock import (
        MockInternalFunctions as InternalFunctions,
    )


router = APIRouter()
templates = Jinja2Templates(directory="templates")


COOKIE_PREFERENCE_KEY = "preference"


@router.get("/", response_class=HTMLResponse, name="problems")
def get_problems(
    request: Request,
    ja: Optional[bool] = None,
    en: Optional[bool] = None,
    hide_solved: Optional[bool] = None,
    level_lower_0: Optional[int] = None,
    level_lower_1: Optional[int] = None,
    contest_type: Optional[int] = None,
    aoj_userid: Optional[str] = None,
    rivals: Optional[str] = None,
) -> Any:
    saved_preference_str: Optional[str] = request.cookies.get(COOKIE_PREFERENCE_KEY)
    if saved_preference_str is None:
        # init with default parameters
        preference = Preference(
            ja=True,
            en=True,
            contest_type=0,
            aoj_userid="",
            rivals=[],
            hide_solved=False,
            level_scopes=[1, 1],
        )
    else:
        preference = Preference(**json.loads(saved_preference_str))

    def update_if_not_none(key: str, var: Any) -> None:
        if var is not None:
            setattr(preference, key, var)

    update_if_not_none("ja", ja)
    update_if_not_none("en", en)
    update_if_not_none("hide_solved", hide_solved)

    if level_lower_0 is not None:
        preference.level_scopes[0] = level_lower_0
    if level_lower_1 is not None:
        preference.level_scopes[1] = level_lower_1

    update_if_not_none("contest_type", contest_type)
    update_if_not_none("aoj_userid", aoj_userid)

    if rivals is not None:
        preference.rivals = [rival for rival in rivals.split(",") if rival]

    if preference.contest_type not in [0, 1]:
        raise HTTPException(status_code=400)

    return _process_request(request, preference)


def _process_request(request: Request, preference: Preference) -> Any:
    functions = InternalFunctions()
    context: dict[str, Any] = {}
    context["preference"] = preference
    context["level_lower"] = preference.level_scopes[preference.contest_type]
    context["points"] = functions.get_points(preference.contest_type)
    context["total_row"] = functions.get_problems_total_row(preference.contest_type)

    userids = set(preference.rivals)
    if preference.aoj_userid:
        userids.add(preference.aoj_userid)
    context["local_ranking"] = functions.get_user_local_ranking(
        preference.contest_type, list(userids)
    )

    user_solved_problems = functions.get_user_solved_problems(preference.aoj_userid)
    context["user_solved_problems"] = user_solved_problems
    context["problems"] = functions.get_problems(preference, user_solved_problems)

    github_login_info = functions.get_github_login_info(request)
    context["github_login_info"] = github_login_info

    if github_login_info is not None:
        context["user_likes"] = functions.get_likes(github_login_info.github_id)
    else:
        context["user_likes"] = set()

    response = templates.TemplateResponse(
        request=request,
        name="problems.html",
        context=context,
    )
    expires = datetime.datetime(2100, 1, 1, tzinfo=datetime.timezone.utc)
    response.set_cookie(
        COOKIE_PREFERENCE_KEY, json.dumps(preference.__dict__), expires=expires
    )
    return response
