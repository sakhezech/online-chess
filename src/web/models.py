import hashlib
import os

import ulid
from sqlalchemy import ForeignKey, String, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)


def _ulid_string() -> str:
    return str(ulid.ULID())


def _hash_password(password: str, salt: bytes) -> bytes:
    hash = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1)
    return hash


class _Base(DeclarativeBase):
    pass


class User(_Base):
    __tablename__ = 'user'
    user_id: Mapped[str] = mapped_column(
        String(26),
        insert_default=_ulid_string,
        primary_key=True,
    )
    username: Mapped[str] = mapped_column(
        String(32),
        index=True,
        unique=True,
    )
    password_hash: Mapped[bytes] = mapped_column()
    password_salt: Mapped[bytes] = mapped_column()

    def __init__(
        self,
        username: str,
        password: str,
    ):
        salt = os.urandom(32)
        self.username = username
        self.password_salt = salt
        self.password_hash = _hash_password(password, salt)

    def validate_password(self, password: str) -> bool:
        hash = _hash_password(password, self.password_salt)
        return self.password_hash == hash


class Session(_Base):
    __tablename__ = 'session'
    session_id: Mapped[str] = mapped_column(
        String(26),
        insert_default=_ulid_string,
        primary_key=True,
    )
    user_id: Mapped[str] = mapped_column(ForeignKey('user.user_id'))
    user: Mapped[User] = relationship()

    def __init__(self, user: User):
        self.user = user


class Chess(_Base):
    __tablename__ = 'chess'
    chess_id: Mapped[str] = mapped_column(
        String(26),
        insert_default=_ulid_string,
        primary_key=True,
    )
    fen: Mapped[str] = mapped_column()
    white_player_id: Mapped[str | None] = mapped_column(
        ForeignKey('user.user_id')
    )
    black_player_id: Mapped[str | None] = mapped_column(
        ForeignKey('user.user_id')
    )
    white_player: Mapped[User | None] = relationship(
        foreign_keys=[white_player_id]
    )
    black_player: Mapped[User | None] = relationship(
        foreign_keys=[black_player_id]
    )
    moves: Mapped[list['Move']] = relationship(back_populates='chess')

    def __init__(
        self,
        white_player: User | None = None,
        black_player: User | None = None,
        fen: str | None = None,
    ):
        self.fen = (
            fen or 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        )
        self.white_player = white_player
        self.black_player = black_player


class Move(_Base):
    __tablename__ = 'move'
    move_id: Mapped[str] = mapped_column(
        String(26),
        insert_default=_ulid_string,
        primary_key=True,
    )
    chess_id: Mapped[str] = mapped_column(ForeignKey('chess.chess_id'))
    user_id: Mapped[str] = mapped_column(ForeignKey('user.user_id'))
    fen: Mapped[str] = mapped_column()
    chess: Mapped[Chess] = relationship(back_populates='moves')
    user: Mapped[User] = relationship()

    def __init__(self, chess: Chess, user: User, fen: str):
        self.chess = chess
        self.user = user
        self.fen = fen


_engine = create_engine('sqlite:///./db.sqlite')
_Base.metadata.create_all(_engine)
DBSession = sessionmaker(_engine)
