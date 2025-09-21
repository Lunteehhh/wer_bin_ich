import json

from fastapi import APIRouter, Form, Depends, Request, Body, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
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

    map_id = maps_service.add_map(user, pack, name)
    map_data = maps_service.get(user, pack, map_id)

    return templates.TemplateResponse("itfd_creator/map_show.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": user,
        "tools": itfd_creator.TOOLS,
        "map_name": name,
        "map_data": map_data,
        "pack": pack
    })


@router.get("/maps/{map_id}", response_class=HTMLResponse)
def show_map(map_id: int,
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

    map_data = maps_service.get(user, pack, map_id)

    print(map_data)

    return templates.TemplateResponse("itfd_creator/map_show.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": user,
        "tools": itfd_creator.TOOLS,
        "map_name": map_id,
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

    return templates.TemplateResponse("itfd_creator/map_node_form.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": user,
        "tools": itfd_creator.TOOLS,

        "node_data": None,
        "node_id": None,
        "map_name": map_name,
        "possible_items": possible_items,
        "possible_monsters": possible_monsters,
        "possible_nodes": possible_nodes,
        "pack": pack,
        "possible_permissions": {0: "Nothing"}
    })


@router.post("/maps/{map_id}/add-node")
async def add_node(
    request: Request,
    map_id: int,
    pack: str,
    node_data: dict = Body(...),
    current_user: dict = Depends(auth.check_access_token)
):
    if current_user["error"]:
        return JSONResponse(
            {"error": "Not logged in"},
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    user = current_user["user_name"]

    maps_service.add_node(user, pack, map_id, **node_data)

    print(f"""
    map:  {map_id}
    pack: {pack}
    user: {user}
    data {node_data}
    """)

    return JSONResponse({
        "status": "ok",
        "redirect_url": f"/itfd-creator/packs/{pack}/maps/{map_id}"
    })


@router.get("/maps/{map_id}/edit-node/{node_id}")
def edit_node_page(request: Request,
                   pack: str,
                   map_id: int,
                   node_id: int,
                   current_user: dict = Depends(auth.check_access_token)):
    if current_user["error"]:
        return JSONResponse(
            {"error": "Not logged in"},
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    user = current_user["user_name"]
    node = maps_service.get_node(user, pack, map_id, node_id)

    print({
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": user,
        "tools": itfd_creator.TOOLS,
        "pack": pack,
        "map_name": map_id,
        "node_data": node.dictionary()
    })
    print(type(request),
          type(user),
          type(itfd_creator.TOOLS),
          type(pack),
          type(map_id),
          type(node.dictionary()))

    return templates.TemplateResponse("itfd_creator/map_node_form.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": user,
        "tools": itfd_creator.TOOLS,
        "pack": pack,
        "map_name": map_id,
        "node_id": node_id,
        "node_data": node.dictionary(),
    })


@router.post("/maps/{map_id}/edit-node/{node_id}")
async def edit_node(
    request: Request,
    pack: str,
    map_id: int,
    node_id: int,
    current_user: dict = Depends(auth.check_access_token)
):
    insert_data = await request.json()
    print(insert_data)
    maps_service.edit_node(current_user["user_name"],
                           pack,
                           map_id,
                           node_id,
                           name=insert_data["name"],
                           category=insert_data["category"],
                           connections=insert_data["connections"],
                           sentences_first=insert_data["sentences_first"],
                           sentences_last=insert_data["sentences_last"],
                           monsters=insert_data["monsters"],
                           items=insert_data["items"],
                           commands=insert_data["commands"],
                           additional_data=insert_data["additional_data"])
    return {
        "status": "ok",
        "redirect_url": f"/itfd-creator/packs/{pack}/maps/ {map_id}"
    }


@router.post("/maps/{map_id}/delete-node/{node_id}")
async def delete_node(request: Request,
                      pack: str,
                      node_id: int,
                      map_id: int,
                      current_user: dict = Depends(auth.check_access_token)):
    if current_user["error"]:
        response = RedirectResponse(url="/you/login", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("user_name")
        return response

    if not pack:
        return RedirectResponse(url="/itfd-creator/", status_code=303)

    user = current_user["user_name"]

    maps_service.delete_node(user, pack, map_id, node_id)

    map_data = maps_service.get(user, pack, map_id)

    return templates.TemplateResponse("itfd_creator/map_show.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": user,
        "tools": itfd_creator.TOOLS,
        "map_name": map_id,
        "map_data": map_data,
        "pack": pack
    })


@router.get("/selectable-nodes", response_class=JSONResponse)
async def possible_nodes(
        pack: str,
        current_user: dict = Depends(auth.check_access_token)
) -> dict[str, int | dict[int, list[str | list]] | None]:
    print(current_user)
    if current_user["error"]:
        return {
            "error": 1,
            "data": None
        }

    if not pack:
        return {
            "error": 2,
            "data": None
        }

    user = current_user["user_name"]

    maps_nodes: dict[int, list[str | list]] = maps_service.possible_nodes(user, pack)

    print("maps-node: ", maps_nodes)
    return {
        "error": 0,
        "data": maps_nodes
    }

