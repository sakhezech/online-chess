from . import pieces as p
from .exceptions import FENError


class Board:
    _CHAR_TO_PIECE = {
        p.Pawn.char: p.Pawn,
        p.Knight.char: p.Knight,
        p.Bishop.char: p.Bishop,
        p.Rook.char: p.Rook,
        p.Queen.char: p.Queen,
        p.King.char: p.King,
    }

    def __init__(self, fen: str | None = None) -> None:
        if fen is None:
            fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        board_fen = fen.split()[0]
        self._board = self._parse_board(board_fen)

    def __repr__(self) -> str:
        reversed_board = list(reversed(self._board))
        board_8x8 = [
            reversed_board[1 + row_num * 10 : 9 + row_num * 10]
            for row_num in range(2, 10)
        ]
        return '\n'.join(
            ' '.join(piece.icon for piece in row) for row in board_8x8
        )

    def _parse_board(self, fen_board: str) -> list[p.Piece]:
        board: list[p.Piece] = []

        rows = len(fen_board.split('/'))
        if rows != 8:
            raise FENError(f'board does not have 8 rows: {rows}')
        # TODO: check if each row has 8 columns

        for _ in range(21):
            board.append(p.Border())

        for char in reversed(fen_board):
            if char.isdigit():
                for _ in range(int(char)):
                    board.append(p.Empty())
            elif char == '/':
                board.append(p.Border())
                board.append(p.Border())
            else:
                if char.lower() not in self._CHAR_TO_PIECE:
                    raise FENError(f'character is not a piece type: {char}')
                color = char.isupper()
                PieceType = self._CHAR_TO_PIECE[char.lower()]
                piece = PieceType(color)
                board.append(piece)

        for _ in range(21):
            board.append(p.Border())

        return board
