from fastapi import FastAPI, Request, Form, Cookie, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import re

import auth
import friends as friends_func

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), "static")
app.mount("/data/friends_pages", StaticFiles(directory="data/friends_pages"), name="data/friends_pages")
templates = Jinja2Templates("templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, user_name: str = Cookie(default=None)):
    return templates.TemplateResponse("home.html", {"request": request, "index_tab": "home", "user_name": user_name})

@app.get("/rules", response_class=HTMLResponse)
async def rules(request: Request, user_name: str = Cookie(default=None)):
    return templates.TemplateResponse("rules.html", {"request": request, "index_tab": "rules", "user_name": user_name})

@app.get("/boring", response_class=HTMLResponse)
async def boring(request: Request, user_name: str = Cookie(default=None)):
    return templates.TemplateResponse("boring.html", {"request": request, "index_tab": "boring", "user_name": user_name})

@app.get("/friends", response_class=HTMLResponse)
async def friends(request: Request, user_name: str = Cookie(default=None)):
    return templates.TemplateResponse("friends.html", {
        "request": request,
        "index_tab": "friends",
        "user_name": user_name,
    })

@app.get("/logout/", response_class=HTMLResponse)
async def logout(request: Request):
    response = RedirectResponse("/login")
    response.delete_cookie("user_name")
    return response


@app.get("/friends/{friend}", response_class=HTMLResponse)
async def friends(request: Request, friend: str, user_name: str = Cookie(default=None)):
    print(friend, user_name)
    return templates.TemplateResponse("friends.html", {
        "request": request,
        "index_tab": "friends",
        "user_name": user_name,
        "friends_page": friend
    })

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "index_tab": "you"})

@app.get("/you", response_class=HTMLResponse)
async def you(request: Request, user_name: str = Cookie(default=None)):
    return templates.TemplateResponse("you.html", {"request": request, "index_tab": "you", "user_name": user_name})

@app.post("/login")
async def login_form(request: Request,
                     action: str = Form(...),
                     name: str = Form(...),
                     password: str = Form(...)):
    if action == "login":
        match auth.check_data(name, password):
            case True:
                response = RedirectResponse(url="/you", status_code=302)
                response.set_cookie("user_name", name)
                return response
            case False:
                return templates.TemplateResponse("login.html", {"request": request, "error_num": 1})
            case None:
                return templates.TemplateResponse("login.html", {"request": request, "error_num": 1})
    elif action == "sign up":
        return templates.TemplateResponse("/login.html", {"request": request, "sign_up": 1, "name": name})

@app.post("/sign_up")
async def sign_up_form(request: Request,
                       action: str = Form(...),
                       name: str = Form(...),
                       password: str = Form(...),
                       password_retry: str = Form(...)):
    if action == "sign up":
        if auth.check_if_username_forgiven(name):
            return templates.TemplateResponse("login.html", {"request": request, "sign_up": 1, "error_num": 1})
        if password_retry != password:
            return templates.TemplateResponse("login.html", {"request": request, "sign_up": 1, "error_num": 2})
        auth.register_new_account(name, password)
        response = RedirectResponse(url="/you", status_code=302)
        response.set_cookie(key="logged_in", value="1")
        response.set_cookie(key="user_name", value=name)
        return response
    elif action == "login":
        return templates.TemplateResponse("login.html", {"request": request, "index_tab": "you"})

@app.post("/upload_html/")
async def upload_html(request: Request,
                      html_file: UploadFile = File(...),
                      user_name: str = Cookie(default=None)):
    contents = await html_file.read()
    contents_string = contents.decode("utf-8")
    contents_string = re.sub(r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>", "", contents_string, flags=re.IGNORECASE)
    with open(f"data/friends_pages/{user_name}.html", "w") as fp:
        fp.write(contents_string)

    return RedirectResponse(url=f"/friends/{user_name}", status_code=303)

@app.post("/search/")
async def search(request: Request,
                 search_bar: str = Form(...),
                 user_name: str = Cookie(default=None)):
    results = friends_func.search(search_bar)
    print(results)
    return templates.TemplateResponse("friends.html", {
        "request": request,
        "index_tab": "friends",
        "user_name": user_name,
        "search_result": results
    })


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)