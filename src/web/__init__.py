from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .htmx import htmx

app = FastAPI()

app.mount('/static', StaticFiles(directory='./static'))
app.include_router(htmx)
