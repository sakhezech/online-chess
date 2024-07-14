from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from . import models as m


def create_user(db: Session, username: str, password: str) -> m.User:
    user = m.User(username, password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_username(db: Session, username: str) -> m.User | None:
    stmt = select(m.User).where(m.User.username == username)
    return db.execute(stmt).scalar()


def get_user_by_session_id(db: Session, session_id: str) -> m.User | None:
    stmt = select(m.Session).where(m.Session.session_id == session_id)
    res = db.execute(stmt).scalar()
    if res is None:
        return None
    return res.user


def create_session(db: Session, user_id: str) -> m.Session:
    sess = m.Session(user_id)
    db.add(sess)
    db.commit()
    db.refresh(sess)
    return sess


def delete_session_by_session_id(db: Session, session_id: str) -> None:
    stmt = delete(m.Session).where(m.Session.session_id == session_id)
    db.execute(stmt)
    db.commit()
