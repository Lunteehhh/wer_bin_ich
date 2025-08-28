import re

from fastapi import APIRouter, Cookie, Request, Depends, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from web_application.core import auth
from web_application.services import friends as friends_func


router = APIRouter(
	prefix="/you",
	tags=["user"]
)

templates = Jinja2Templates("web_application/templates")


# user manager
@router.get("/", response_class=HTMLResponse)
async def you(request: Request,
			  current_user: dict = Depends(auth.check_access_token)):
	if current_user["error"]:
		response = RedirectResponse(url="/login", status_code=303)
		response.delete_cookie("access_token")
		response.delete_cookie("user_name")
		return response

	friends_page = friends_func.search(current_user["user_name"])[0][1]
	return templates.TemplateResponse("you.html", {
		"request": request,
		"index_tab": "you",
		"user_name": current_user["user_name"],
		"friends_page": friends_page
	})


@router.post("/upload_html/")
async def upload_html(request: Request,
					  html_file: UploadFile = File(...),
					  user_name: str = Cookie(default=None),
					  action: str = Form(...)):
	if action == "upload":

		if html_file.size == 0:
			friends_page = friends_func.search(user_name)[0][1]
			return templates.TemplateResponse("you.html", {
				"request": request,
				"index_tab": "you",
				"user_name": user_name,
				"friends_page": friends_page
			})

		contents = await html_file.read()
		contents_string = contents.decode("utf-8")
		contents_string = re.sub(r"<script\b[^<]*(?:(?!</script>)<[^<]*)*</script>",
								 "", contents_string, flags=re.IGNORECASE)
		with open(f"web_application/data/friends_pages/{user_name}.html", "w") as fp:
			fp.write(contents_string)

		friends_func.update_friends_page(user_name,
										 f"/data/friends_pages/{user_name}.html")
		return RedirectResponse(url=f"/friends/{user_name}", status_code=303)
	else:
		friends_func.update_friends_page(user_name)
		return RedirectResponse(url=f"/friends/{user_name}", status_code=303)


# Login and Register
@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
	return templates.TemplateResponse("login.html", {
		"request": request,
		"index_tab": "you"
	})


@router.post("/login")
async def login_form(request: Request,
					 action: str = Form(...),
					 name: str = Form(...),
					 password: str = Form(...)):
	if action == "login":
		match auth.check_data(name, password):
			case True:
				response = RedirectResponse(url="/you", status_code=302)
				token = auth.create_token({"sub": name})
				response.set_cookie("access_token", token, httponly=True)
				response.set_cookie("user_name", name)
				return response
			case False:
				return templates.TemplateResponse("login.html", {
					"request": request,
					"error_num": 1
				})
			case None:
				return templates.TemplateResponse("login.html", {
					"request": request,
					"error_num": 1
				})
	elif action == "sign up":
		return templates.TemplateResponse("login.html", {
			"request": request,
			"sign_up": 1,
			"name": name
		})


@router.get("/sign-up", response_class=HTMLResponse)  # user auth
async def sign_up(request: Request):
	return templates.TemplateResponse("login.html", {
		"request": request,
		"index_tab": "you",
		"sign_up": True
	})


@router.post("/sign_up")
async def sign_up_form(request: Request,
					   action: str = Form(...),
					   name: str = Form(...),
					   password: str = Form(...),
					   password_retry: str = Form(...)):
	if action == "sign up":
		if auth.check_if_username_forgiven(name):
			return templates.TemplateResponse("login.html", {
				"request": request,
				"sign_up": 1,
				"error_num": 1
			})
		if password_retry != password:
			return templates.TemplateResponse("login.html", {
				"request": request,
				"sign_up": 1,
				"error_num": 2
			})
		auth.register_new_account(name, password)
		friends_func.add(name)
		response = RedirectResponse(url="/you", status_code=302)
		token = auth.create_token({"sub": name})
		response.set_cookie("access_token", token, httponly=True)
		response.set_cookie("user_name", name)

		return response
	else:
		return templates.TemplateResponse("login.html", {
			"request": request,
			"index_tab": "you"
		})


# Logout and Delete account
@router.post("/delete-account/")  # user
async def delete_account(request: Request,
						 user_name: str = Cookie(default=None)):
	friends_func.remove(user_name)
	auth.remove(user_name)
	response = RedirectResponse(url="/you/login", status_code=303)
	response.delete_cookie("user_name")
	response.delete_cookie("access_token")
	return response


@router.post("/logout/")
async def logout(request: Request):
	response = RedirectResponse(url="/you/login", status_code=302)
	response.delete_cookie("user_name")
	response.delete_cookie("access_token")
	return response
