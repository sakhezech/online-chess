from typing import Literal

from chess.board import Board
from chess.color import BLACK, WHITE
from chess.exceptions import IllegalMoveError
from chess.pieces import Border, Piece
from chess.util import index_to_square
from fastapi import WebSocket

from . import crud
from . import models as m

_ = WHITE, BLACK
Mode = Literal['htmx', 'json']


class ChessManager:
    def __init__(self, chess_id: str) -> None:
        self.db = m.DBSession()

        chess = crud.get_chess_by_chess_id(self.db, chess_id)
        if chess is None:
            raise ValueError

        self.chess = chess
        self.board = Board(chess.fen)
        self.connections: list[WebSocket] = []
        self.ws_mode: dict[WebSocket, Mode] = {}

        self.update_board_responses()

    async def move(
        self,
        ws: WebSocket,
        user: m.User | None,
        data: dict,
    ) -> None:
        if not user or (
            user.user_id != self.chess.white_player_id
            and user.user_id != self.chess.black_player_id
        ):
            await self.send_notification(ws, 'you are a spectator')
            return

        current_player = (
            self.chess.white_player
            if self.board.active_color == WHITE
            else self.chess.black_player
        )
        if not current_player or user.user_id != current_player.user_id:
            await self.send_notification(ws, "it's not your turn")
            return

        try:
            move = data['move']
            self.board.move_uci(move)
            fen = self.board.fen()
            self.chess.fen = fen
            self.commit_chess_changes()
            self.update_board_responses()
            crud.create_move(self.db, self.chess.chess_id, user.user_id, fen)
        except IllegalMoveError:
            await self.send_notification(ws, 'illegal move')
        except ValueError:
            await self.send_notification(ws, 'invalid move')
        else:
            await self.broadcast_board()

    def commit_chess_changes(self) -> None:
        self.db.commit()
        self.db.refresh(self.chess)

    async def connect(
        self,
        ws: WebSocket,
        user: m.User | None,
        mode: Mode,
    ) -> None:
        await ws.accept()
        self.connections.append(ws)
        self.ws_mode[ws] = mode

        if user:
            if not self.chess.white_player:
                self.chess.white_player_id = user.user_id
                self.commit_chess_changes()
            elif (
                not self.chess.black_player
                and user.user_id != self.chess.white_player.user_id
            ):
                self.chess.black_player_id = user.user_id
                self.commit_chess_changes()

        await self.send_board(ws)

    async def disconnect(self, ws: WebSocket) -> None:
        self.connections.remove(ws)
        self.ws_mode.pop(ws)

        if not self.connections:
            MANAGERS.pop(self.chess.chess_id)
            self.db.close()

    async def broadcast_board(self) -> None:
        for ws in self.connections:
            await self.send_board(ws)

    async def send_board(self, ws: WebSocket) -> None:
        mode = self.ws_mode[ws]
        if mode == 'json':
            await ws.send_json({'type': 'board', 'data': self.json_board})
        elif mode == 'htmx':
            await ws.send_text(
                f"""
                <div id="board">{self.htmx_board}</div>
                <div id="notification"></div>
                """
            )

    async def broadcast_notification(self, text: str) -> None:
        for ws in self.connections:
            await self.send_notification(ws, text)

    async def send_notification(self, ws: WebSocket, text: str) -> None:
        mode = self.ws_mode[ws]
        if mode == 'json':
            await ws.send_json({'type': 'notification', 'data': text})
        elif mode == 'htmx':
            await ws.send_text(f'<div id="notification">{text}</div>')

    def update_board_responses(self) -> None:
        json_board = {}
        html_squares = []
        square_is_white = False

        for i, piece in enumerate(self.board):
            if isinstance(piece, Border):
                continue

            json_board[index_to_square(i)] = {
                'piece': type(piece).__name__,
                'color': piece.color.name if isinstance(piece, Piece) else '',
            }

            if i % 10 == 1:
                square_is_white = not square_is_white

            html_squares.append(
                f"""
                <div id="{i}"
                  class="{'white' if square_is_white else 'black'}">
                  {piece.icon}
                </div>
                """
            )
            square_is_white = not square_is_white

        htmx_board = ''.join(html_squares)
        self.htmx_board = htmx_board
        self.json_board = json_board


MANAGERS: dict[str, ChessManager] = {}
