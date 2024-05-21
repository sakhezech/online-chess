import contextlib

from . import pieces as p
from .exceptions import FENError, NotAPieceError
from .util import CastleRights, Move, index_to_square, square_to_index


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
        (
            board,
            active_color,
            castle_rights,
            en_passant,
            halfmoves,
            fullmoves,
        ) = fen.split()

        self._board = self._parse_board(board)
        self.active_color = self._parse_active_color(active_color)
        self.castle_rights = self._parse_castle_rights(castle_rights)
        self.en_passant = self._parse_en_passant(en_passant)
        self.fullmoves = self._parse_fullmoves(fullmoves)
        self.halfmoves = self._parse_halfmoves(halfmoves)
        self._pieces = self._get_pieces()
        self.legal_moves = self._get_legal_moves_for_active_color()

    def __repr__(self) -> str:
        board_8x8 = [
            self._board[1 + row_num * 10 : 9 + row_num * 10]
            for row_num in range(2, 10)
        ]
        return '\n'.join(
            ' '.join(piece.icon for piece in row) for row in board_8x8
        )

    def __iter__(self):
        return self._board.__iter__()

    def __getitem__(self, __key: str | int):
        if isinstance(__key, str):
            __key = square_to_index(__key)
        return self._board[__key]

    def __setitem__(
        self, __key: str | int, __item: p.Piece | p.Empty | p.Border
    ):
        if isinstance(__key, str):
            __key = square_to_index(__key)
        self._board[__key] = __item

    def _parse_active_color(self, active_color: str) -> bool:
        if active_color == 'w':
            return True
        elif active_color == 'b':
            return False
        raise FENError(f"active color is not 'w' or 'b': {active_color}")

    def _parse_en_passant(self, en_passant: str) -> int:
        if en_passant == '-':
            return 0
        return square_to_index(en_passant)

    def _parse_castle_rights(
        self, castle_rights: str
    ) -> dict[bool, CastleRights]:
        if castle_rights == '-':
            return {
                True: CastleRights(False, False),
                False: CastleRights(False, False),
            }
        return {
            True: CastleRights('K' in castle_rights, 'Q' in castle_rights),
            False: CastleRights('k' in castle_rights, 'q' in castle_rights),
        }

    def _parse_fullmoves(self, fullmoves: str) -> int:
        try:
            fm = int(fullmoves)
        except ValueError:
            raise FENError(f'fullmove counter is not a number: {fullmoves}')
        if fm < 1:
            raise FENError(f'fullmove counter is less than 1: {fullmoves}')
        return fm

    def _parse_halfmoves(self, halfmoves: str) -> int:
        try:
            hm = int(halfmoves)
        except ValueError:
            raise FENError(f'halfmove clock is not a number: {halfmoves}')
        if not 0 <= hm <= 100:
            raise FENError(
                f'halfmove clock is below 0 or above 100: {halfmoves}'
            )
        return hm

    def _parse_board(
        self, fen_board: str
    ) -> list[p.Piece | p.Empty | p.Border]:
        board = []

        rows = len(fen_board.split('/'))
        if rows != 8:
            raise FENError(f'board does not have 8 rows: {rows}')
        # TODO: check if each row has 8 columns

        for _ in range(21):
            board.append(p.Border())

        for char in fen_board:
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

    def _get_pieces(self) -> dict[bool, set[p.Piece]]:
        white_pieces = set()
        black_pieces = set()
        for piece in self:
            if isinstance(piece, p.Piece):
                if piece.color:
                    white_pieces.add(piece)
                else:
                    black_pieces.add(piece)
        return {True: white_pieces, False: black_pieces}

    def _is_in_check(self, color: bool):
        kings = {
            king for king in self._pieces[color] if isinstance(king, p.King)
        }
        enemy_types = {type(piece) for piece in self._pieces[not color]}
        return any(
            Type.threatens_index(self._board.index(king), self)
            for king in kings
            for Type in enemy_types
        )

    def move(self, move: str) -> None:
        move_ = Move.from_uci(move)
        if move_ not in self.legal_moves:
            raise ValueError
        self._move(move_)
        self.active_color = not self.active_color
        if self.active_color:
            self.fullmoves += 1
        self.legal_moves = self._get_legal_moves_for_active_color()

    def _move(self, move: Move, bookkepp: bool = True) -> None:
        index = move.origin
        piece = self._board[index]
        if not isinstance(piece, p.Piece):
            raise NotAPieceError(f'not a piece: {index_to_square(index)}')
        piece.make_move(move, self, bookkepp)

    @contextlib.contextmanager
    def with_move(self, move: Move):
        board = self._board
        self._board = board.copy()
        self._move(move, False)
        yield
        self._board = board

    def _get_pseudolegal_moves_by_index(self, index: int) -> set[Move]:
        piece = self._board[index]
        if not isinstance(piece, p.Piece):
            raise NotAPieceError(f'not a piece: {index_to_square(index)}')
        return piece.get_pseudolegal_moves(self, index)

    def _get_pseudolegal_moves_by_square(self, square: str) -> set[Move]:
        index = square_to_index(square)
        return self._get_pseudolegal_moves_by_index(index)

    def _get_legal_moves_by_index(self, index: int) -> set[Move]:
        piece = self._board[index]
        if not isinstance(piece, p.Piece):
            raise NotAPieceError(f'not a piece: {index_to_square(index)}')
        return piece.get_legal_moves(self, index)

    def _get_legal_moves_by_square(self, square: str) -> set[Move]:
        index = square_to_index(square)
        return self._get_legal_moves_by_index(index)

    def _get_legal_moves_for_active_color(self) -> set[Move]:
        moves = set()
        for piece in self._pieces[self.active_color]:
            index = self._board.index(piece)
            moves.update(piece.get_legal_moves(self, index))
        return moves
