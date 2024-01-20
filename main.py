from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import ijproblems.routers.apis.like as like
import ijproblems.routers.pages.problems as problems
import ijproblems.routers.pages.statistics as statistics
import ijproblems.routers.pages.user as user

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(problems.router)
app.include_router(statistics.router)
app.include_router(user.router)
app.include_router(like.router)
