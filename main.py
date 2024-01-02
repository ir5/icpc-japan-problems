import os

from fastapi import FastAPI

app = FastAPI()

if os.environ.get("IJARCHIVE_USE_MOCK_API"):
    import ijarchive.routers.mock_apis.mock as mock
    app.include_router(mock.router)


@app.get("/")
def root():
    return {"message": "Hello World From Fast API!"}
