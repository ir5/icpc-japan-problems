import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import ijarchive.routers.pages.problems as problems

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

if os.environ.get("IJARCHIVE_USE_MOCK_API"):
    import ijarchive.routers.mock_apis.mock as mock

    app.include_router(mock.router)

app.include_router(problems.router)


@app.get("/")
def root():
    return {"message": "Hello World From Fast API!"}
