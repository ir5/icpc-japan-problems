import datetime
import json
from typing import Any, Optional

import psycopg
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ijproblems.internal_functions import get_internal_functions
from ijproblems.internal_functions.github_app import GITHUB_APP_CLIENT_ID
from ijproblems.internal_functions.interface import Preference
from ijproblems.routers.utils.cookie import (
    COOKIE_PREFERENCE_KEY,
    get_preference_from_cookie,
)
from ijproblems.routers.utils.database import get_db_conn

router = APIRouter()
templates = Jinja2Templates(directory="templates")


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
    conn: psycopg.Connection = Depends(get_db_conn),
) -> Any:
    preference = get_preference_from_cookie(request)

    def update_if_not_none(key: str, var: Any) -> None:
        if var is not None:
            setattr(preference, key, var)

    update_if_not_none("ja", ja)
    update_if_not_none("en", en)
    update_if_not_none("hide_solved", hide_solved)

    if level_lower_0 is not None:
        preference.level_scopes[0] = level_lower_0
    else:
        preference.level_scopes[0] = -1
    if level_lower_1 is not None:
        preference.level_scopes[1] = level_lower_1
    else:
        preference.level_scopes[1] = -1

    update_if_not_none("contest_type", contest_type)
    update_if_not_none("aoj_userid", aoj_userid)

    if rivals is not None:
        preference.rivals = [rival for rival in rivals.split(",") if rival]

    if preference.contest_type not in [0, 1]:
        raise HTTPException(status_code=400)

    return _process_request(request, preference, conn)


def _process_request(
    request: Request, preference: Preference, conn: psycopg.Connection
) -> Any:
    functions = get_internal_functions(conn)
    context: dict[str, Any] = {}
    context["preference"] = preference
    context["level_lower"] = preference.level_scopes[preference.contest_type]
    context["points"] = functions.get_points(preference.contest_type)
    context["total_row"] = functions.get_problems_total_row(preference.contest_type)

    userids = set(name.lower() for name in preference.rivals)
    if preference.aoj_userid:
        userids.add(preference.aoj_userid.lower())
    context["local_ranking"] = functions.get_user_local_ranking(
        preference.contest_type, list(userids)
    )

    user_solved_problems = functions.get_user_solved_problems(preference.aoj_userid)
    context["user_solved_problems"] = user_solved_problems
    context["problems"] = functions.get_problems(preference, user_solved_problems)

    github_login_info = functions.get_github_login_info(request)
    context["github_login_info"] = github_login_info
    context["github_app_client_id"] = GITHUB_APP_CLIENT_ID

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
