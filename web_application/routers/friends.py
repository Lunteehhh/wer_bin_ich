from fastapi import APIRouter, Request, Cookie, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from web_application.services import friends as friends_func


router = APIRouter(
	prefix="/friends",
	tags=["friends"]
)

templates = Jinja2Templates("web_application/templates")


@router.get("/", response_class=HTMLResponse)  # friends
async def friends(request: Request,
				  user_name: str =
				  Cookie(default=None)):
	return templates.TemplateResponse("friends.html", {
		"request": request,
		"index_tab": "friends",
		"user_name": user_name
	})


@router.post("/search/")  # friends
async def search(request: Request,
				 search_bar: str = Form(...),
				 user_name: str = Cookie(default=None)):
	results = friends_func.search(search_bar)
	return templates.TemplateResponse("friends.html", {
		"request": request,
		"index_tab": "friends",
		"user_name": user_name,
		"search_result": results,
		"results_count": len(results),
		"friends_count": friends_func.friends_count
	})


@router.get("/friends-page", response_class=HTMLResponse)
async def friends_page(request: Request,
					   name: str):
	return templates.TemplateResponse("empty_page.html", {
		"request": request,
		"name": name
	})


@router.get("/{friend}", response_class=HTMLResponse)
async def friends(request: Request,
				  friend: str,
				  user_name: str = Cookie(default=None)):
	friends_page = friends_func.get_friends_page(friend)[0]
	return templates.TemplateResponse("friends.html", {
		"request": request,
		"index_tab": "friends",
		"user_name": user_name,
		"friends_page": friends_page
	})
