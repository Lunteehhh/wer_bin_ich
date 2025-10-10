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

    return templates.TemplateResponse("itfd_creator/items/item_index.html", {
        "request": request,
        "index_tab": "itfd-creator",
        "user_name": current_user["user_name"],
        "tools": itfd_creator.TOOLS,
        "items": fetched_items,
        "pack": pack
    })


@router.get("/items/{item_id}")
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
        f"itfd_creator/items/item_show_{item_data[1]}.html",
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
    return templates.TemplateResponse("itfd_creator/items/item_add.html", {
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

    return templates.TemplateResponse("itfd_creator/items/item_edit.html", {
        "request": request,
        "item": item,
        "tools": itfd_creator.TOOLS,
        "index_tab": "itfd-creator",
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


"""
Luck Nums
################################################################################
"""


@router.get("/luck-num", response_class=HTMLResponse)
def luck_num_index(request: Request,
                   pack: str,
                   current_user: dict = Depends(auth.check_access_token)):
    user = current_user["user_name"]

    luck_nums = item_service.get_all_luck_num(pack, user)

    return templates.TemplateResponse(
        "itfd_creator/items/luck_num_index.html",
        {
            "request": request,
            "index_tab": "itfd-creator",
            "tools": itfd_creator.TOOLS,
            "user_name": user,
            "pack": pack,

            "luck_nums": luck_nums
        }
    )


@router.get("/luck-num/{luck_num}", response_class=HTMLResponse)
def luck_num_index(request: Request,
                   pack: str,
                   luck_num: int,
                   current_user: dict = Depends(auth.check_access_token)):
    user = current_user["user_name"]

    _, minor_luck_nums, drops = item_service.get_luck_num(pack, user, luck_num)
    linkages = item_service.get_luck_num_linkages(user, pack, luck_num)

    return templates.TemplateResponse(
        "itfd_creator/items/luck_num_show.html",
        {
            "request": request,
            "index_tab": "itfd-creator",
            "tools": itfd_creator.TOOLS,
            "user_name": user,
            "pack": pack,

            "luck_num": luck_num,
            "minor_luck_nums": minor_luck_nums,
            "drops": drops,
            "linkages": linkages
        }
    )


@router.get("/add-luck-num", response_class=HTMLResponse)
def add_luck_num(request: Request,
                 pack: str,
                 current_user: dict = Depends(auth.check_access_token)):
    user = current_user["user_name"]

    return templates.TemplateResponse(
        "itfd_creator/items/luck_num_form.html",
        {
            "request": request,
            "index_tab": "itfd-creator",
            "tools": itfd_creator.TOOLS,
            "user_name": user,
            "pack": pack,

            "luck_num": None,
            "luck_num_data": None
        }
    )


@router.post("/add-luck-num")
async def post_add_luck_num(request: Request,
                            pack: str,
                            current_user: dict = Depends(auth.check_access_token)):
    data = await request.json()

    print(data)
    user = current_user["user_name"]

    item_service.add_luck_num(user,
                              pack,
                              data["luckNum"],
                              data["minorLuckNums"],
                              data["drops"])

    return {
        "status": "ok",
        "redirect_url": f"/itfd-creator/packs/{pack}"
    }


@router.get("/edit-luck-num/{luck_num}")
def edit_luck_num(request: Request,
                  pack: str,
                  luck_num: int,
                  current_user: dict = Depends(auth.check_access_token)):
    user = current_user["user_name"]

    data = item_service.get_luck_num(pack, user, luck_num)
    print(data)

    return templates.TemplateResponse(
        "itfd_creator/items/luck_num_form.html",
        {
            "request": request,
            "index_tab": "itfd-creator",
            "tools": itfd_creator.TOOLS,
            "user_name": user,
            "pack": pack,

            "luck_num": luck_num,
            "luck_num_data": data
        }
    )


@router.post("/edit-luck-num/{luck_num}")
async def edit_luck_num_post(request: Request,
                             pack: str,
                             luck_num: int,
                             current_user=Depends(auth.check_access_token)):
    data = await request.json()

    print(data)
    user = current_user["user_name"]

    item_service.edit_luck_num(user,
                               pack,
                               luck_num,
                               data["luckNum"],
                               data["minorLuckNums"],
                               data["drops"])

    return {
        "status": "ok",
        "redirect_url": f"/itfd-creator/packs/{pack}"
    }


@router.post("/delete-luck-num/{luck_num}", response_class=RedirectResponse)
def delete_luck_num(request: Request,
                    pack: str,
                    luck_num: int,
                    current_user=Depends(auth.check_access_token)):
    user = current_user["user_name"]

    item_service.delete_luck_num(user, pack, luck_num)

    return RedirectResponse(url=f"/itfd-creator/packs/{pack}/luck-num",
                            status_code=303)


@router.get("/selectable-luck-nums")
def possible_luck_nums(pack: str,
                       current_user=Depends(auth.check_access_token)):
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

    user = current_user["user_name"]
    possible_luck_nums = item_service.get_possible_luck_nums(pack, user)

    print(possible_luck_nums)

    return {
        "error": 0,
        "data": possible_luck_nums
    }
