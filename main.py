import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

import ijproblems.routers.apis.like as like
import ijproblems.routers.apis.github_callback as github_callback
import ijproblems.routers.pages.problems as problems
import ijproblems.routers.pages.statistics as statistics
import ijproblems.routers.pages.user as user
import ijproblems.routers.pages.ranking as ranking

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(github_callback.router)
app.include_router(like.router)
app.include_router(problems.router)
app.include_router(statistics.router)
app.include_router(user.router)
app.include_router(ranking.router)

secret = os.environ.get("SESSION_SECRET", "ija")
app.add_middleware(SessionMiddleware, secret_key=secret)
