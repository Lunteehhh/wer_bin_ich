from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from web_application.core import auth, itfd_creator
from web_application.services.itfd_creator import (monsters as monster_service,
                                                   items as item_service)

router = APIRouter(
    prefix="/itfd-creator/pack/{pack}",
    tags=["itfd-creator", "monsters"]
)

templates = Jinja2Templates("web_application/templates")


@router.get("/monsters", response_class=HTMLResponse)
def monsters_index(request: Request,
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
    fetched_monsters = monster_service.monsters(user, pack)
    print(fetched_monsters)

    return templates.TemplateResponse("itfd_creator/monster_index.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": current_user["user_name"],
        "tools": itfd_creator.TOOLS,
        "monsters": fetched_monsters,
        "pack": pack
    })


@router.get("/{monster}",
            response_class=HTMLResponse)
def monster_show(request: Request,
                 monster: str,
                 pack: str,
                 current_user: dict = Depends(auth.check_access_token)):
    if current_user["error"]:
        response = RedirectResponse(url="/you/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    user = current_user["user_name"]

    monster_data = monster_service.get(user, pack, monster)
    if not monster:
        return HTMLResponse(content="Monster not found!", status_code=404)

    linkage_maps = monster_service.get_linkage(user, pack, monster)
    return templates.TemplateResponse("itfd_creator/monster_show.html", {
        "request": request,
        "monster": monster_data,
        "linkage_maps": linkage_maps,
        "pack": pack
    })


@router.get("/add-monster",
            response_class=HTMLResponse)
def add_monster_page(request: Request,
                     pack: str,
                     current_user: dict = Depends(auth.check_access_token)):
    if current_user["error"]:
        response = RedirectResponse(url="/you/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    user = current_user["user_name"]

    possible_items = item_service.possible_items(user, pack)

    return templates.TemplateResponse("itfd_creator/monster_add.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": user,
        "tools": itfd_creator.TOOLS,
        "possible_items": possible_items,
        "pack": pack
    })


@router.post("/add-monster")
def add_monster(pack: str,
                current_user: dict = Depends(auth.check_access_token),
                name: str = Form(...),
                strength: int = Form(...),
                health: int = Form(...),
                xp: int = Form(...),
                items: list[int] = Form([]),
                sentences: list[str] = Form([])):
    if current_user["error"]:
        response = RedirectResponse(url="/you/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack:
        return RedirectResponse(url="/itfd-creator", status_code=303)

    user = current_user["user_name"]

    not_existing_items = item_service.check_if_items_exists(user, pack, items)
    if not_existing_items:
        return

    monster_service.add(user, pack,
                        name, health, strength, xp, items, sentences)

    return RedirectResponse(url=f"/monsters",
                            status_code=303)


@router.get("/edit-monster/{monster}",
            response_class=HTMLResponse)
def edit_monster_page(request: Request,
                      monster: str,
                      pack: str,
                      current_user: dict = Depends(auth.check_access_token)):
    if current_user["error"]:
        response = RedirectResponse(url="/you/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    user = current_user["user_name"]

    monster = monster_service.get(user, pack, monster)
    if not monster:
        return HTMLResponse(content="Monster nicht gefunden!", status_code=404)

    possible_items = item_service.possible_items(user, pack)
    return templates.TemplateResponse("itfd_creator/monster_edit.html", {
        "request": request,
        "monster": monster,
        "possible_items": possible_items,
        "pack": pack
    })


@router.post("/edit-monster/{monster}")
def edit_monster_post(request: Request,
                      pack: str,
                      monster: str,
                      current_user: dict = Depends(auth.check_access_token),
                      name: str = Form(...),
                      strength: int = Form(...),
                      health: int = Form(...),
                      xp: int = Form(...),
                      items: list[int] = Form([]),
                      sentences: list[str] = Form([])):
    if current_user["error"]:
        response = RedirectResponse(url="/you/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    user = current_user["user_name"]
    if not monster_service.check_if_monster_exists(user, pack, monster):
        return HTMLResponse(content="Monster wasn't found!", status_code=404)

    monster_service.edit(user, pack,
                         name, health, strength, xp, items, sentences)

    monster_service.edit(user, pack, monster,
                         health, strength, xp, items, sentences,
                         name if name != monster else None)

    fetched_monsters = monster_service.monsters(user, pack)

    return templates.TemplateResponse("itfd_creator/monster_index.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": current_user["user_name"],
        "tools": itfd_creator.TOOLS,
        "monsters": fetched_monsters,
        "pack": pack
    })


@router.post("/delete-monster/{monster}")
def delete_monster(monster: str,
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
    monster_service.delete(user, pack, monster)

    return RedirectResponse(url="/itfd-creator/monster", status_code=303)
