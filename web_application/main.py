from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import uvicorn

from web_application.core import auth
from web_application.services import friends as friends_servie

from web_application.routers.general import router as general_router
from web_application.routers.user import router as user_router
from web_application.routers.friends import router as friends_router

from web_application.routers.itfd_creator import pack, items, monsters, maps


class NoCacheStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response


app = FastAPI()


# Mounts und templates
app.mount("/static",
          NoCacheStaticFiles(directory="web_application/static"),
          "static")
app.mount("/friends_pages",
          StaticFiles(directory="data/friends_pages"),
          name="friends_pages")


# Routers
app.include_router(general_router)
app.include_router(user_router)
app.include_router(friends_router)

# itfd-creator Routers
app.include_router(pack.router)
app.include_router(items.router)
app.include_router(monsters.router)
app.include_router(maps.router)


def init():
    friends_servie.init()
    auth.init()


if __name__ == "__main__":
    init()

    uvicorn.run("main:app",
                host="127.0.0.1",
                port=8000,
                reload=True)
