import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import ijproblems.routers.apis.like as like
import ijproblems.routers.pages.problems as problems

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

if os.environ.get("IJPROBLEMS_USE_MOCK_API"):
    import ijproblems.routers.mock_apis.mock as mock

    app.include_router(mock.router)

app.include_router(problems.router)
app.include_router(like.router)
