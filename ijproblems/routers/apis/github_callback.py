from typing import Any

import requests
import starlette.status as status
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from ijproblems.internal_functions.github_app import (
    GITHUB_APP_CLIENT_ID,
    GITHUB_APP_CLIENT_SECRET,
)

router = APIRouter()


@router.get(
    "/api/github/callback", response_class=RedirectResponse, name="github_callback"
)
def github_callback(request: Request, code: str) -> Any:
    data = {
        "client_id": GITHUB_APP_CLIENT_ID,
        "client_secret": GITHUB_APP_CLIENT_SECRET,
        "code": code,
    }
    headers = {"Accept": "application/json"}
    oauth_uri = "https://github.com/login/oauth/access_token"
    response = requests.post(oauth_uri, data=data, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="invalid response from oauth")

    try:
        access_token_data = response.json()
        token = access_token_data["access_token"]
    except Exception:
        raise HTTPException(status_code=401, detail="response from oauth is broken")

    user_uri = "https://api.github.com/user"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    response = requests.get(user_uri, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="invalid response from user")

    try:
        user = response.json()
        request.session["github_login"] = user["login"]
        request.session["github_id"] = user["id"]
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    except Exception:
        raise HTTPException(status_code=401, detail="response from user is broken")
