import os
from typing import Optional, Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ijarchive.internal_functions_interface import Preference

if os.environ.get("USE_MOCK"):
    from ijarchive.mock_functions.mock import MockInternalFunctions as InternalFunctions


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse, name="problems")
def get_problems(request: Request,
                 ja: Optional[bool] = True,
                 en: Optional[bool] = True,
                 hide_solved: Optional[bool] = False,
                 level_lower_0: Optional[int] = 1,
                 level_lower_1: Optional[int] = 1,
                 contest_type: Optional[int] = 0,
                 aoj_userid: Optional[str] = "",
                 rivals: Optional[str] = "",
                 ):
    level_scopes = [level_lower_0, level_lower_1]
    rivals_list = [rival for rival in rivals.split(",") if rival]

    preference = Preference(
        ja=ja,
        en=en,
        contest_type=contest_type,
        aoj_userid=aoj_userid,
        rivals=rivals_list,
        hide_solved=hide_solved,
        level_scopes=level_scopes
    )

    functions = InternalFunctions()
    context: dict[str, Any] = {}
    context["preference"] = preference
    context["level_lower"] = level_scopes[contest_type]
    context["points"] = functions.get_points(contest_type)
    context["problems"] = functions.get_problems(preference)
    context["total_row"] = functions.get_problems_total_row(contest_type)

    userids = set(rivals_list)
    if aoj_userid:
        userids.add(aoj_userid)
    context["local_ranking"] = functions.get_user_local_ranking(contest_type, list(userids))

    return templates.TemplateResponse(
        request=request, name="problems.html", context=context,
    )
