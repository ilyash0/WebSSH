from os import environ

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import static
from app.routes import index, panel

routers = (index.router, panel.router,)
load_dotenv()
app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory=static.__path__[0]),
    name="static",
)
app.add_middleware(SessionMiddleware, secret_key=environ["SECRET_KEY"])

for router in routers:
    app.include_router(router)
