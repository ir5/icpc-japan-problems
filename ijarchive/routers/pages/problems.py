import os
from typing import Optional, Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ijarchive.internal_functions_interface import LevelScope, Preference

if os.environ.get("USE_MOCK"):
    from ijarchive.mock_functions.mock import MockInternalFunctions as InternalFunctions


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse, name="problems")
def get_problems(request: Request, 
                 ja: Optional[bool] = True,
                 en: Optional[bool] = True,
                 hide_solved: Optional[bool] = False,
                 point_lower_0: Optional[int] = 1,
                 point_upper_0: Optional[int] = 11,
                 point_lower_1: Optional[int] = 1,
                 point_upper_1: Optional[int] = 9,
                 contest_type: Optional[int] = 0,
                 aoj_userid: Optional[str] = "",
                 rivals: Optional[str] = "",
                ):
    rivals_list = rivals.split(",")
    level_scopes = [LevelScope(point_lower_0, point_upper_0), LevelScope(point_lower_1, point_upper_1)]

    preference = Preference(
        contest_type=contest_type,
        aoj_userid=aoj_userid,
        rivals=rivals_list,
        exclude_solved=hide_solved,
        level_scopes=level_scopes
    )

    functions = InternalFunctions()
    context: dict[str, Any] = {}
    context["points"] = functions.get_points(contest_type)
    context["problems"] = functions.get_problems(preference)
    context["total_row"] = functions.get_problems_total_row(contest_type)

    userids = rivals_list
    if aoj_userid:
        userids.append(aoj_userid)
    # functions.get_user_local_ranking(userids)

    return templates.TemplateResponse(
        request=request, name="problems.html", context=context,
    )
