from fastapi import APIRouter, Form, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from web_application.core import auth, itfd_creator
from web_application.services.itfd_creator import (maps as maps_service,
                                                   items as item_service,
                                                   monsters as monster_service)

router = APIRouter(
    prefix="/itfd-creator/packs/{pack}",
    tags=["itfd-creator", "packs"]
)

templates = Jinja2Templates("web_application/templates")


@router.get("/maps", response_class=HTMLResponse)
def maps_page(request: Request,
              pack: str,
              current_user: dict = Depends(auth.check_access_token)):
    if current_user["error"]:
        response = RedirectResponse(url="/you/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack:
        return RedirectResponse(url="/itfd-creator/", status_code=303)
    user = current_user["user_name"]

    maps = maps_service.maps(user, pack)

    return templates.TemplateResponse("itfd_creator/map_page.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": user,
        "tools": itfd_creator.TOOLS,
        "maps": maps,
        "pack": pack
    })


@router.get("/add-map")
def add_map(request: Request,
            pack: str,
            current_user: dict = Depends(auth.check_access_token)):
    if current_user["error"]:
        response = RedirectResponse(url="/you/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack:
        return RedirectResponse(url="/itfd-creator/", status_code=303)
    user = current_user["user_name"]

    return templates.TemplateResponse("itfd_creator/map_add.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": user,
        "tools": itfd_creator.TOOLS,
        "pack": pack
    })


@router.post("/add-map")
def add_map(request: Request,
            pack: str,
            current_user: dict = Depends(auth.check_access_token),
            name: str = Form(...)):
    if current_user["error"]:
        response = RedirectResponse(url="/you/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack:
        return RedirectResponse(url="/itfd-creator", status_code=303)
    user = current_user["user_name"]

    maps_service.add(user, pack, name)
    map_data = maps_service.get(user, pack, name)

    return templates.TemplateResponse("itfd_creator/map_show.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": user,
        "tools": itfd_creator.TOOLS,
        "map_name": name,
        "map_data": map_data,
        "pack": pack
    })


@router.get("/maps/{map_name}",
            response_class=HTMLResponse)
def show_map(map_name: str,
             request: Request,
             pack: str,
             current_user: dict = Depends(auth.check_access_token)):
    if current_user["error"]:
        response = RedirectResponse(url="/you/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack:
        return RedirectResponse(url="/itfd-creator/", status_code=303)
    user = current_user["user_name"]

    map_data = maps_service.get(user, pack, map_name)

    return templates.TemplateResponse("itfd_creator/map_show.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": user,
        "tools": itfd_creator.TOOLS,
        "map_name": map_name,
        "map_data": map_data,
        "pack": pack
    })


@router.get("/maps/{map_name}/add-node")
def add_node_page(request: Request,
                  map_name: str,
                  pack: str,
                  current_user: dict = Depends(auth.check_access_token)):
    if current_user["error"]:
        response = RedirectResponse(url="/you/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack:
        return RedirectResponse(url="/itfd-creator/", status_code=303)
    user = current_user["user_name"]

    possible_items = item_service.possible_items(user, pack)
    possible_monsters = monster_service.possible_monsters(user, pack)
    possible_nodes = maps_service.possible_nodes(user, pack)

    return templates.TemplateResponse("itfd_creator/map_add_node.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": user,
        "tools": itfd_creator.TOOLS,
        "map_name": map_name,
        "possible_items": possible_items,
        "possible_monsters": possible_monsters,
        "possible_nodes": possible_nodes,
        "pack": pack,
        "possible_permissions": {0: "Nothing"}
    })


@router.post("/maps/{map_name}/add-node")
async def add_node(
    request: Request,
    map_name: str,
    pack: str,
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
        response = RedirectResponse(url="/you/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack:
        return RedirectResponse(url="/itfd-creator", status_code=303)

    user = current_user["user_name"]

    # Build connections
    connections = list(zip(connections_node_name,
                           connections_title,
                           connections_permission))

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
        user, pack, map_name,
        name, category,
        connections,
        sentences_first, sentences_last,
        monsters, items,
        commands,
        additional_data
    )

    map_data = maps_service.get(user, pack, map_name)

    return templates.TemplateResponse("itfd_creator/map_show.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": user,
        "tools": itfd_creator.TOOLS,
        "map_name": map_name,
        "map_data": map_data,
        "pack": pack
    })


@router.get("/maps/{map_name}/edit-node/{node_name}")
def edit_node_page(request: Request,
                   pack: str,
                   map_name: str,
                   node_name: str,
                   current_user: dict = Depends(auth.check_access_token)):
    if current_user["error"]:
        response = RedirectResponse(url="/you/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack:
        return RedirectResponse(url="/itfd-creator/", status_code=303)
    user = current_user["user_name"]

    node = maps_service.get_node(user, pack, map_name, node_name)
    print(node)

    possible_items = item_service.possible_items(user, pack)
    possible_monsters = monster_service.possible_monsters(user, pack)
    possible_nodes = maps_service.possible_nodes(user, pack)

    import json

    x = {
        "map_name": map_name,
        "node_data": node.dictionary(),
        "possible_items": possible_items,
        "possible_monsters": possible_monsters,
        "possible_nodes": possible_nodes,
        "pack": pack,
        "possible_permissions": {0: "Nothing"},
        "possible_commands": {0: "Nothing"}
    }
    print(x)

    x = json.dumps(x)

    with open("data.json", "w") as file:
        file.write(x)

    return templates.TemplateResponse("itfd_creator/map_edit_node.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": user,
        "tools": itfd_creator.TOOLS,
        "map_name": map_name,
        "node_data": node,
        "possible_items": possible_items,
        "possible_monsters": possible_monsters,
        "possible_nodes": possible_nodes,
        "pack": pack,
        "possible_permissions": {0: "Nothing"},
        "possible_commands": {0: "Nothing"}
    })


@router.post("/maps/{map_name}/edit-node/{node_name}")
async def add_node(
    request: Request,
    pack: str,
    node_name: str,
    map_name: str,
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
        response = RedirectResponse(url="/you/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack:
        return RedirectResponse(url="/itfd-creator/", status_code=303)

    user = current_user["user_name"]

    # Build connections
    connections = list(zip(connections_node_name,
                           connections_title,
                           connections_permission))

    # Build additional_data only if category == 1
    additional_data = None
    if category == 1:
        additional_data = list(zip(
            additional_map_name,
            additional_node_name,
            additional_title,
            additional_permission
        ))

        print(user, pack, map_name, node_name,
              name, category,
              connections,
              sentences_first, sentences_last,
              monsters, items,
              commands,
              additional_data)

    maps_service.edit_node(
        user, pack, map_name, node_name,
        name, category,
        connections,
        sentences_first, sentences_last,
        monsters, items,
        commands,
        additional_data
    )

    map_data = maps_service.get(user, pack, map_name)

    return templates.TemplateResponse("itfd_creator/map_show.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": user,
        "tools": itfd_creator.TOOLS,
        "map_name": map_name,
        "map_data": map_data,
        "pack": pack
    })


@router.post("/maps/{map_name}/delete-node/{node_name}")
async def delete_node(request: Request,
                      pack: str,
                      node_name: str,
                      map_name: str,
                      current_user: dict = Depends(auth.check_access_token)):
    if current_user["error"]:
        response = RedirectResponse(url="/you/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack:
        return RedirectResponse(url="/itfd-creator/", status_code=303)

    user = current_user["user_name"]

    maps_service.delete_node(user, pack, map_name, node_name)

    map_data = maps_service.get(user, pack, map_name)

    return templates.TemplateResponse("itfd_creator/map_show.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": user,
        "tools": itfd_creator.TOOLS,
        "map_name": map_name,
        "map_data": map_data,
        "pack": pack
    })
