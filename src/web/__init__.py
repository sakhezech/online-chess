from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .api import api_v1
from .htmx import htmx

app = FastAPI()

app.mount('/static', StaticFiles(directory='./static'))
app.include_router(htmx)
app.include_router(api_v1)
