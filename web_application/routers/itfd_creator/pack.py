from fastapi import APIRouter, Form, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from web_application.core import auth, itfd_creator
from web_application.services.itfd_creator import (utils)

router = APIRouter(
    prefix="/itfd-creator",
    tags=["itfd-creator", "pack"]
)

templates = Jinja2Templates("web_application/templates")

print(templates.__dict__)


@router.get("/", response_class=HTMLResponse)
def pack_selector(request: Request,
                  current_user: dict = Depends(auth.check_access_token)):
    """Übersichtsseite für den ITFD Creator."""
    if current_user["error"]:
        response = RedirectResponse(url="/you/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    packs = utils.get_packs(current_user["user_name"])
    return templates.TemplateResponse("itfd_creator/pack_select.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": current_user["user_name"],
        "tools": itfd_creator.TOOLS,
        "packs": packs
    })


@router.get("/new-pack")
def pack_new_page(request: Request,
                  current_user: dict = Depends(auth.check_access_token)):
    if current_user["error"]:
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    return templates.TemplateResponse("itfd_creator/pack_new.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": current_user["user_name"],
        "tools": itfd_creator.TOOLS
    })


@router.post("/new-pack")
def pack_new_post(request: Request,
                  name: str = Form(...),
                  current_user: dict = Depends(auth.check_access_token)):
    """Neuen Pack erstellen oder bestehenden Pack auswählen."""
    if current_user["error"]:
        response = RedirectResponse(url="/you/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    user = current_user["user_name"]
    packs = utils.get_packs(user)

    if name in packs:
        response = RedirectResponse(url="/itfd-creator/",
                                    status_code=303)
        response.set_cookie(key="error", value="Pack exist!")
        return response

    utils.add_new_pack(user, name)

    return templates.TemplateResponse("itfd_creator/pack_index.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": user,
        "tools": itfd_creator.TOOLS,
        "pack": name
    })


@router.get("/packs/{pack}", response_class=HTMLResponse)
def pack_page(request: Request,
              pack: str,
              current_user: dict = Depends(auth.check_access_token)):
    if current_user["error"]:
        response = RedirectResponse(url="/you/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    user = current_user["user_name"]

    return templates.TemplateResponse("itfd_creator/pack_index.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": user,
        "tools": itfd_creator.TOOLS,
        "pack": pack
    })


@router.post("/delete-pack/{pack}")
def pack_delete_post(request: Request,
                     pack: str,
                     current_user: dict = Depends(auth.check_access_token)):
    """Neuen Pack erstellen oder bestehenden Pack auswählen."""
    if current_user["error"]:
        response = RedirectResponse(url="/you/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    user = current_user["user_name"]

    utils.delete_pack(user, pack)

    return templates.TemplateResponse("itfd_creator/pack_select.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": user,
        "tools": itfd_creator.TOOLS,
        "pack": pack
    })
