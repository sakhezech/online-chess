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


def create_chess(db: Session, fen: str | None = None) -> m.Chess:
    chess = m.Chess(fen=fen)
    db.add(chess)
    db.commit()
    db.refresh(chess)
    return chess


def get_chess_by_chess_id(db: Session, chess_id: str) -> m.Chess | None:
    stmt = select(m.Chess).where(m.Chess.chess_id == chess_id)
    return db.execute(stmt).scalar()


def create_move(db: Session, chess_id: str, user_id: str, fen: str) -> m.Move:
    move = m.Move(chess_id, user_id, fen)
    db.add(move)
    db.commit()
    db.refresh(move)
    return move
