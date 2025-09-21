from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from web_application.core import auth, itfd_creator
from web_application.services.itfd_creator import items as item_service


router = APIRouter(
    prefix="/itfd-creator/packs/{pack}",
    tags=["itfd-creator", "items"]
)

templates = Jinja2Templates("web_application/templates")


@router.get("/items", response_class=HTMLResponse)
async def items_index(request: Request,
                      pack: str,
                      current_user: dict = Depends(auth.check_access_token)):
    """Alle Items eines Packs anzeigen."""
    if current_user["error"]:
        response = RedirectResponse(url="/you/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack:
        return RedirectResponse(url="/itfd-creator/", status_code=303)

    user = current_user["user_name"]
    fetched_items = item_service.items(user, pack)

    return templates.TemplateResponse("itfd_creator/item_index.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": current_user["user_name"],
        "tools": itfd_creator.TOOLS,
        "items": fetched_items,
        "pack": pack
    })


@router.get("items/{item_id}")
def item_show(request: Request,
              pack: str,
              item_id: int,
              current_user: dict = Depends(auth.check_access_token)):
    if current_user["error"]:
        response = RedirectResponse(url="/you/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    user = current_user["user_name"]
    item_data = item_service.get(user, pack, item_id)

    linkages = item_service.get_linkage(user, pack, item_id)
    linkage_monsters, linkage_maps = linkages

    return templates.TemplateResponse(
        f"itfd_creator/item_show_{item_id}.html",
        {
            "request": request,
            "index_tab": "itfd-creator",
            "user_name": current_user["user_name"],
            "tools": itfd_creator.TOOLS,
            "pack": pack,
            "item": item_data,
            "linkage_monsters": linkage_monsters,
            "linkage_maps": linkage_maps
        }
    )


@router.get("/add-item", response_class=HTMLResponse)
def add_item_form(request: Request,
                  pack: str,
                  current_user: dict = Depends(auth.check_access_token)):
    return templates.TemplateResponse("itfd_creator/item_add.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": current_user["user_name"],
        "tools": itfd_creator.TOOLS,
        "pack": pack
    })


@router.post("/add-item")
async def add_item(pack: str,
                   name: str = Form(...),
                   category: int = Form(...),
                   a: int = Form(None),
                   b: int = Form(None),
                   c: int = Form(None),
                   d: int = Form(None),
                   e: int = Form(None),
                   current_user: dict = Depends(auth.check_access_token)):
    """Item hinzufügen."""
    if current_user["error"]:
        response = RedirectResponse(url="/you/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack:
        return RedirectResponse(url="/itfd-creator/", status_code=303)

    user = current_user["user_name"]
    item_service.add(user, pack, name, category, a, b, c, d, e)

    return RedirectResponse(url=f"/itfd-creator/packs/{pack}/items",
                            status_code=303)


@router.get("/edit-item/{item_id}", response_class=HTMLResponse)
def edit_item_form(request: Request,
                   item_id: int,
                   pack: str,
                   current_user: dict = Depends(auth.check_access_token)):
    """Formular zum Bearbeiten eines Items."""
    if current_user["error"]:
        response = RedirectResponse(url="/you/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack:
        return RedirectResponse(url="/itfd-creator/", status_code=303)

    user = current_user["user_name"]
    fetched_items = item_service.items(user, pack)
    item = next((i for i in fetched_items if i[0] == item_id), None)

    if not item:
        return HTMLResponse("Item not found", status_code=404)

    return templates.TemplateResponse("itfd_creator/item_edit.html", {
        "request": request,
        "item": item,
        "tools": itfd_creator.TOOLS,
        "user_name": user,
        "pack": pack
    })


@router.post("edit-item/{item_id}")
def edit_item_post(item_id: int,
                   pack: str,
                   name: str = Form(...),
                   category: int = Form(...),
                   a: int = Form(None),
                   b: int = Form(None),
                   c: int = Form(None),
                   d: int = Form(None),
                   e: int = Form(None),
                   current_user: dict = Depends(auth.check_access_token)):
    """Änderungen an einem Item speichern."""
    if current_user["error"]:
        response = RedirectResponse(url="/you/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack:
        return RedirectResponse(url="/itfd-creator/", status_code=303)

    user = current_user["user_name"]
    item_service.edit(user, pack, item_id, name, category, a, b, c, d, e)

    return RedirectResponse(url=f"/itfd-creator/packs/{pack}/items",
                            status_code=303)


@router.post("/delete-item/{item_id}")
def delete_item(item_id: int,
                pack: str,
                current_user: dict = Depends(auth.check_access_token)):
    """Ein Item löschen."""
    if current_user["error"]:
        response = RedirectResponse(url="/you/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack:
        return RedirectResponse(url="/itfd-creator/", status_code=303)

    user = current_user["user_name"]
    item_service.delete(user, pack, item_id)

    return RedirectResponse(url=f"/itfd-creator/packs/{pack}/items",
                            status_code=303)


@router.get("/selectable-items")
async def selectable_items(pack: str,
                           current_user: dict = Depends(auth.check_access_token)
                           ) -> dict[str, int | list[tuple[int, str]] | None]:
    if current_user["error"]:
        response = RedirectResponse(url="/you/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return {
            "error": 401,
            "data": None
        }

    if not pack:
        return {
            "error": 400,
            "data": None
        }

    possible_items = item_service.possible_items(current_user["user_name"],
                                                 pack)
    return {
        "error": 0,
        "data": possible_items
    }
