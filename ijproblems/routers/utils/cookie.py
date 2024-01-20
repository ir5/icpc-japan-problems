import json
from typing import Optional

from fastapi import Request

from ijproblems.internal_functions.interface import Preference

COOKIE_PREFERENCE_KEY = "preference"


def get_preference_from_cookie(request: Request) -> Preference:
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

    return preference
