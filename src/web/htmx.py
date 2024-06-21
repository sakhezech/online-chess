from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Form, Response
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from . import crud, deps
from . import models as m
from .renderer import render

htmx = APIRouter(
    default_response_class=HTMLResponse,
    include_in_schema=False,
)


def set_session_cookie(response: Response, session: m.Session) -> None:
    response.set_cookie(
        'session',
        session.session_id,
        secure=True,
        httponly=True,
        samesite='lax',
    )


@htmx.get('/')
async def index(user: m.User | None = Depends(deps.get_current_user)):
    return render('index', user)


@htmx.get('/login')
async def login_page(
    user: m.User | None = Depends(deps.get_current_user),
):
    return render('login', user)


@htmx.post('/login')
async def login(
    response: Response,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: Session = Depends(deps.get_db),
):
    user = crud.get_user_by_username(db, username)
    if user and user.validate_password(password):
        sess = crud.create_session(db, user)
        set_session_cookie(response, sess)
        response.headers['HX-Redirect'] = '/'


@htmx.post('/register')
async def register(
    response: Response,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    repeat: Annotated[str, Form()],
    db: Session = Depends(deps.get_db),
):
    if password == repeat:
        user = crud.create_user(db, username, password)
        sess = crud.create_session(db, user)
        set_session_cookie(response, sess)
        response.headers['HX-Redirect'] = '/'


@htmx.post('/logoff')
async def logoff(
    response: Response,
    session: Annotated[str, Cookie()],
    db: Session = Depends(deps.get_db),
):
    crud.delete_session_by_session_id(db, session)
    response.delete_cookie('session')
    response.headers['HX-Refresh'] = 'true'
