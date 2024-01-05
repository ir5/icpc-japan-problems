from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse, name="problems")
def read_item(request: Request):
    return templates.TemplateResponse(
        request=request, name="problems.html", context={"id": 123}
    )
