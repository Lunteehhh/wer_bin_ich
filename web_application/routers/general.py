from fastapi import APIRouter, Cookie, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
	tags=["general"]
)

templates = Jinja2Templates("web_application/templates")


@router.get("/", response_class=HTMLResponse)  # general
async def home(request: Request, user_name: str = Cookie(default=None)):
	return templates.TemplateResponse("home.html", {
		"request": request,
		"index_tab": "home",
		"user_name": user_name
	})


@router.get("/rules", response_class=HTMLResponse)  # general
async def rules(request: Request, user_name: str = Cookie(default=None)):
	return templates.TemplateResponse("rules.html", {
		"request": request,
		"index_tab": "rules",
		"user_name": user_name
	})


@router.get("/boring", response_class=HTMLResponse)
async def boring(request: Request, user_name: str = Cookie(default=None)):
	return templates.TemplateResponse("boring.html", {
		"request": request,
		"index_tab": "boring",
		"user_name": user_name
	})


@router.get("/dsgvo", response_class=HTMLResponse)
async def dsgvo(request: Request, user_name: str = Cookie(default=None)):
	return templates.TemplateResponse("dsgvo.html", {
		"request": request,
		"index_tab": "home",
		"user_name": user_name,
		"name": user_name
	})


@router.get("/impressum", response_class=HTMLResponse)
async def impressum(request: Request, user_name: str = Cookie(default=None)):
	return templates.TemplateResponse("impressum.html", {
		"request": request,
		"index_tab": "home",
		"user_name": user_name
	})


