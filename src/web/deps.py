from typing import Annotated

from fastapi import Cookie, Depends
from sqlalchemy.orm import Session

from . import crud
from . import models as m


async def get_db():
    db = m.DBSession()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    session: Annotated[str | None, Cookie()] = None,
    db: Session = Depends(get_db),
) -> m.User | None:
    if session is None:
        return None
    return crud.get_user_by_session_id(db, session)
