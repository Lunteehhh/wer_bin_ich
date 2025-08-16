
from fastapi import APIRouter, Request, Cookie, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

import auth
from services.itfd_creator import utils
from services.itfd_creator import items as item_service
from services.itfd_creator import monsters as monster_service
from services.itfd_creator import maps as maps_service


# Templates
templates = Jinja2Templates(directory="templates")

router = APIRouter()

# Werkzeugstruktur
TOOLS = [
    {
        "name": "Items",
        "url": "/itfd-creator/items",
        "subtools": [
            {"name": "Add", "url": "/itfd-creator/add-item"},
            {"name": "Edit", "url": "/itfd-creator/edit-item"},
            {"name": "Delete", "url": "/itfd-creator/delete-item"},
            {"name": "Show", "url": "/itfd-creator/show-item"}
        ]
    },
    {
        "name": "Monsters",
        "url": "/tools/console",
        "subtools": [
            {"name": "Add", "url": "/tools/editor/text"},
            {"name": "Edit", "url": "/tools/editor/code"},
            {"name": "Show", "url": "/tools/editor/code"}
        ]
    },
    {
        "name": "Logger",
        "url": "/tools/logger",
        "subtools": [
            {"name": "Add", "url": "/tools/editor/text"},
            {"name": "Edit", "url": "/tools/editor/code"},
            {"name": "Show", "url": "/tools/editor/code"}
        ]
    }
]


@router.get("/itfd-creator", response_class=HTMLResponse)
def pack_editor(request: Request,
                current_user: dict = Depends(auth.check_access_token)):
    """Übersichtsseite für den ITFD Creator."""
    if current_user["error"]:
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    packs = utils.get_packs(current_user["user_name"])
    return templates.TemplateResponse(
        "itfd_creator/index.html",
        {
            "request": request,
            "index_tab": "itfd-creator",
            "user_name": current_user["user_name"],
            "tools": TOOLS,
            "packs": packs
        }
    )


@router.post("/itfd-creator/add-pack")
def post_pack_creator(
    pack_option: str = Form(...),
    existing_pack: str = Form(None),
    new_pack: str = Form(None),
    current_user: dict = Depends(auth.check_access_token)
):
    """Neuen Pack erstellen oder bestehenden Pack auswählen."""
    if current_user["error"]:
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    user = current_user["user_name"]
    packs = utils.get_packs(user)

    if pack_option == "existing":
        chosen_pack = existing_pack
    else:
        if new_pack in packs:
            response = RedirectResponse(url="/itfd-creator/add-pack",
                                        status_code=303)
            response.set_cookie(key="error", value="Pack existiert bereits!",
                                max_age=5)
            return response

        packs.append(new_pack)
        chosen_pack = new_pack
        utils.add_new_pack(user, new_pack)

    response = RedirectResponse(url="/itfd-creator", status_code=303)
    response.set_cookie(key="pack_name", value=chosen_pack, max_age=3600,
                        httponly=True)
    return response


@router.get("/itfd-creator/add-item", response_class=HTMLResponse)
def add_item_form(request: Request,
                  pack_name: str = Cookie(default=None),
                  current_user: dict = Depends(auth.check_access_token)):
    """Formular zum Hinzufügen eines Items anzeigen."""
    if not pack_name:
        return RedirectResponse(url="/itfd-creator", status_code=303)

    return templates.TemplateResponse("itfd_creator/add_item.html", {
            "request": request,
            "index_tab": "itfd-creator",
            "user_name": current_user["user_name"],
            "tools": TOOLS,
        })


@router.post("/itfd-creator/add-item")
async def add_item(name: str = Form(...),
                   category: int = Form(...),
                   a: int = Form(None),
                   b: int = Form(None),
                   c: int = Form(None),
                   d: int = Form(None),
                   e: int = Form(None),
                   pack_name: str = Cookie(default=None),
                   current_user: dict = Depends(auth.check_access_token)):
    """Item hinzufügen."""
    if current_user["error"]:
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack_name:
        return RedirectResponse(url="/itfd-creator", status_code=303)

    user = current_user["user_name"]
    item_service.add(user, pack_name, name, category, a, b, c, d, e)

    return RedirectResponse(url="/itfd-creator/items", status_code=303)


@router.get("/itfd-creator/items", response_class=HTMLResponse)
async def items_index(request: Request,
                      pack_name: str = Cookie(default=None),
                      current_user: dict = Depends(auth.check_access_token)):
    """Alle Items eines Packs anzeigen."""
    if current_user["error"]:
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack_name:
        return RedirectResponse(url="/itfd-creator", status_code=303)

    user = current_user["user_name"]
    fetched_items = item_service.items(user, pack_name)

    return templates.TemplateResponse(
        "itfd_creator/items_index.html",
        {
            "request": request,
            "index_tab": "itfd-creator",
            "user_name": current_user["user_name"],
            "tools": TOOLS,
            "items": fetched_items
        }
    )


@router.get("/itfd-creator/edit-item/{item_id}", response_class=HTMLResponse)
def edit_item_form(request: Request,
                   item_id: int,
                   pack_name: str = Cookie(default=None),
                   current_user: dict = Depends(auth.check_access_token)):
    """Formular zum Bearbeiten eines Items."""
    if current_user["error"]:
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack_name:
        return RedirectResponse(url="/itfd-creator", status_code=303)

    user = current_user["user_name"]
    fetched_items = item_service.items(user, pack_name)
    item = next((i for i in fetched_items if i[0] == item_id), None)

    if not item:
        return HTMLResponse("Item not found", status_code=404)

    return templates.TemplateResponse(
        "itfd_creator/edit_item.html",
        {
            "request": request,
            "item": item,
            "tools": TOOLS,
            "user_name": user,
        }
    )


@router.post("/itfd-creator/edit-item/{item_id}")
def edit_item(
    item_id: int,
    name: str = Form(...),
    category: int = Form(...),
    a: int = Form(None),
    b: int = Form(None),
    c: int = Form(None),
    d: int = Form(None),
    e: int = Form(None),
    pack_name: str = Cookie(default=None),
    current_user: dict = Depends(auth.check_access_token)
):
    """Änderungen an einem Item speichern."""
    if current_user["error"]:
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack_name:
        return RedirectResponse(url="/itfd-creator", status_code=303)

    user = current_user["user_name"]
    item_service.edit(user, pack_name, item_id, name, category, a, b, c, d, e)

    return RedirectResponse(url="/itfd-creator/items", status_code=303)


@router.post("/itfd-creator/delete-item/{item_id}")
def delete_item(
    item_id: int,
    pack_name: str = Cookie(default=None),
    current_user: dict = Depends(auth.check_access_token)
):
    """Ein Item löschen."""
    if current_user["error"]:
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack_name:
        return RedirectResponse(url="/itfd-creator", status_code=303)

    user = current_user["user_name"]
    item_service.delete(user, pack_name, item_id)

    return RedirectResponse(url="/itfd-creator/items", status_code=303)


@router.get("/itfd-creator/monsters", response_class=HTMLResponse)
def monsters_index(request: Request,
                   pack_name: str = Cookie(default=None),
                   current_user: dict = Depends(auth.check_access_token)):
    """Alle Items eines Packs anzeigen."""
    if current_user["error"]:
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack_name:
        return RedirectResponse(url="/itfd-creator", status_code=303)

    user = current_user["user_name"]
    fetched_monsters = monster_service.monsters(user, pack_name)
    print(fetched_monsters)

    return templates.TemplateResponse("itfd_creator/monster_index.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": current_user["user_name"],
        "tools": TOOLS,
        "monsters": fetched_monsters
    })


@router.get("/itfd-creator/add-monster", response_class=HTMLResponse)
def add_monster_page(request: Request,
                    pack_name: str = Cookie(default=None),
                    current_user: dict = Depends(auth.check_access_token)):
    if current_user["error"]:
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    user = current_user["user_name"]

    possible_items = item_service.possible_items(user, pack_name)

    return templates.TemplateResponse("itfd_creator/monster_add.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": user,
        "tools": TOOLS,
        "possible_items": possible_items
    })


@router.post("/itfd-creator/add-monster")
def add_monster(request: Request,
                pack_name: str = Cookie(default=None),
                current_user: dict = Depends(auth.check_access_token),
                name: str = Form(...),
                strength: int = Form(...),
                health: int = Form(...),
                xp: int = Form(...),
                items: list[int] = Form([]),
                sentences: list[str] = Form([])):
    if current_user["error"]:
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack_name:
        return RedirectResponse(url="/itfd-creator", status_code=303)

    user = current_user["user_name"]

    not_existing_items = item_service.check_if_items_exists(user, pack_name,
                                                            items)
    if not_existing_items:
        return

    monster_service.add(user, pack_name,
                        name, health, strength, xp, items, sentences)

    return RedirectResponse(url="/itfd-creator/monsters", status_code=303)


@router.get("/itfd-creator/edit-monster/{monster}", response_class=HTMLResponse)
def edit_monster_page(request: Request,
                      monster: str,
                      pack_name: str = Cookie(default=None),
                      current_user: dict = Depends(auth.check_access_token)):
    if current_user["error"]:
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    user = current_user["user_name"]

    monster = monster_service.get(user, pack_name, monster)
    if not monster:
        return HTMLResponse(content="Monster nicht gefunden!", status_code=404)

    possible_items = item_service.possible_items(user, pack_name)
    return templates.TemplateResponse("itfd_creator/monster_edit.html", {
        "request": request,
        "monster": monster,
        "possible_items": possible_items
    })


@router.post("/itfd-creator/edit-monster/{monster}")
def edit_monster_post(request: Request,
                      monster: str,
                      pack_name: str = Cookie(default=None),
                      current_user: dict = Depends(auth.check_access_token),
                      name: str = Form(...),
                      strength: int = Form(...),
                      health: int = Form(...),
                      xp: int = Form(...),
                      items: list[int] = Form([]),
                      sentences: list[str] = Form([])):
    if current_user["error"]:
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    user = current_user["user_name"]
    if not monster_service.check_if_monster_exists(user, pack_name, monster):
        return HTMLResponse(content="Monster wasn't found!", status_code=404)

    monster_service.edit(user, pack_name,
                         name, health, strength, xp, items, sentences)

    monster_service.edit(user, pack_name, monster,
                         health, strength, xp, items, sentences,
                         name if name != monster else None)

    fetched_monsters = monster_service.monsters(user, pack_name)

    return templates.TemplateResponse("itfd_creator/monster_index.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": current_user["user_name"],
        "tools": TOOLS,
        "monsters": fetched_monsters,
    })


@router.post("/itfd-creator/delete-monster/{monster}")
def delete_monster(monster: str,
                   pack_name: str = Cookie(default=None),
                   current_user: dict = Depends(auth.check_access_token)):
    """Ein Item löschen."""
    if current_user["error"]:
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack_name:
        return RedirectResponse(url="/itfd-creator", status_code=303)

    user = current_user["user_name"]
    monster_service.delete(user, pack_name, monster)

    return RedirectResponse(url="/itfd-creator/monster", status_code=303)


@router.get("/itfd-creator/maps", response_class=HTMLResponse)
def maps_page(request: Request,
              pack_name: str = Cookie(default=None),
              current_user: dict = Depends(auth.check_access_token)):
    if current_user["error"]:
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack_name:
        return RedirectResponse(url="/itfd-creator", status_code=303)
    user = current_user["user_name"]

    maps = maps_service.maps(user, pack_name)

    return templates.TemplateResponse("itfd_creator/maps_page.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": user,
        "tools": TOOLS,
        "maps": maps
    })


@router.get("/itfd-creator/add-map")
def add_map(request: Request,
            pack_name: str = Cookie(default=None),
            current_user: dict = Depends(auth.check_access_token)):
    if current_user["error"]:
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack_name:
        return RedirectResponse(url="/itfd-creator", status_code=303)
    user = current_user["user_name"]

    return templates.TemplateResponse("itfd_creator/maps_add.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": user,
        "tools": TOOLS,
    })


@router.post("/itfd-creator/add-map")
def add_map(request: Request,
            pack_name: str = Cookie(default=None),
            current_user: dict = Depends(auth.check_access_token),
            name: str = Form(...)):
    if current_user["error"]:
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack_name:
        return RedirectResponse(url="/itfd-creator", status_code=303)
    user = current_user["user_name"]

    maps_service.add(user, pack_name, name)

    return RedirectResponse(url=f"/itfd-creator/maps/{name}")


@router.get("/itfd-creator/maps/{map_name}", response_class=HTMLResponse)
def show_map(map_name: str,
             request: Request,
             pack_name: str = Cookie(default=None),
             current_user: dict = Depends(auth.check_access_token)):

    if current_user["error"]:
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack_name:
        return RedirectResponse(url="/itfd-creator", status_code=303)
    user = current_user["user_name"]

    map_data = maps_service.get(user, pack_name, map_name)

    return templates.TemplateResponse("itfd_creator/maps_show.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": user,
        "tools": TOOLS,
        "map_name": map_name,
        "map_data": map_data
    })


@router.get("/itfd-creator/maps/{map_name}/add-node")
def add_node_page(request: Request,
                  map_name: str,
                  pack_name: str = Cookie(default=None),
                  current_user: dict = Depends(auth.check_access_token)):
    if current_user["error"]:
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack_name:
        return RedirectResponse(url="/itfd-creator", status_code=303)
    user = current_user["user_name"]

    possible_items = item_service.possible_items(user, pack_name)
    possible_monsters = monster_service.possible_monsters(user, pack_name)
    possible_nodes = maps_service.possible_nodes(user, pack_name)

    return templates.TemplateResponse("itfd_creator/maps_add_node.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": user,
        "tools": TOOLS,
        "map_name": map_name,
        "possible_items": possible_items,
        "possible_monsters": possible_monsters,
        "possible_nodes": possible_nodes
    })


@router.post("/itfd-creator/maps/{map_name}/add-node")
async def add_node(
    request: Request,
    map_name: str,
    pack_name: str = Cookie(default=None),
    current_user: dict = Depends(auth.check_access_token),

    # basic fields
    name: str = Form(...),
    category: int = Form(...),

    # additional_data (only if category == 1)
    additional_map_name: list[str] = Form(default=[]),
    additional_node_name: list[str] = Form(default=[]),
    additional_title: list[str] = Form(default=[]),
    additional_permission: list[int] = Form(default=[]),
):
    form = await request.form()
    sentences_first = form.getlist("sentences_first[]")
    sentences_last = form.getlist("sentences_last[]")
    connections_node_name = form.getlist("connections_node_name[]")
    connections_title = form.getlist("connections_title[]")
    connections_permission = [int(x) for x in
                              form.getlist("connections_permission[]")]
    items = list(map(int, form.getlist("items[]")))
    monsters = form.getlist("monsters[]")
    commands = [int(x) for x in form.getlist("commands[]")]

    if current_user["error"]:
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack_name:
        return RedirectResponse(url="/itfd-creator", status_code=303)

    user = current_user["user_name"]

    # Build connections
    connections = list(zip(connections_node_name, connections_title, connections_permission))

    # Build additional_data only if category == 1
    additional_data = None
    if category == 1:
        additional_data = list(zip(
            additional_map_name,
            additional_node_name,
            additional_title,
            additional_permission
        ))

    maps_service.add_node(
        user, pack_name, map_name,
        name, category,
        connections,
        sentences_first, sentences_last,
        monsters, items,
        commands,
        additional_data
    )

    map_data = maps_service.get(user, pack_name, map_name)

    return templates.TemplateResponse("itfd_creator/maps_show.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": user,
        "tools": TOOLS,
        "map_name": map_name,
        "map_data": map_data
    })
