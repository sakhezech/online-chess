import contextlib

from . import pieces as p
from . import status
from .color import BLACK, WHITE, Color
from .exceptions import FENError, IllegalMoveError, NotAPieceError
from .util import CastleRights, Move, index_to_square, square_to_index


class Board:
    _PIECE_TYPES = {p.Pawn, p.Knight, p.Bishop, p.Rook, p.Queen, p.King}
    _PAWN_PROMOTIONS = {p.Knight, p.Bishop, p.Rook, p.Queen}
    _COLORS = [WHITE, BLACK]

    def __init__(self, fen: str | None = None) -> None:
        self._CHAR_TO_PIECE = {Type.char: Type for Type in self._PIECE_TYPES}
        self._CHAR_TO_PROMOTION = {
            Type.char: Type for Type in self._PAWN_PROMOTIONS
        }
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
        self._total_halfmoves = self._COLORS.index(self.active_color)
        self.castle_rights = self._parse_castle_rights(castle_rights)
        self.en_passant = self._parse_en_passant(en_passant)
        self.fullmoves = self._parse_fullmoves(fullmoves)
        self.halfmoves = self._parse_halfmoves(halfmoves)
        self._pieces = self._get_sets_of_pieces_by_color()
        self.legal_moves = self._get_legal_moves_for_active_color()
        self.status = self._get_status()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.fen()}')"

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

    def _parse_active_color(self, active_color: str) -> Color:
        if active_color == 'w':
            return WHITE
        elif active_color == 'b':
            return BLACK
        raise FENError(f"active color is not 'w' or 'b': {active_color}")

    def _parse_en_passant(self, en_passant: str) -> int:
        if en_passant == '-':
            return 0
        return square_to_index(en_passant)

    def _parse_castle_rights(
        self, castle_rights: str
    ) -> dict[Color, CastleRights]:
        if castle_rights == '-':
            return {
                WHITE: CastleRights(False, False),
                BLACK: CastleRights(False, False),
            }
        return {
            WHITE: CastleRights('K' in castle_rights, 'Q' in castle_rights),
            BLACK: CastleRights('k' in castle_rights, 'q' in castle_rights),
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
                color = WHITE if char.isupper() else BLACK
                PieceType = self._CHAR_TO_PIECE[char.lower()]
                piece = PieceType(color)
                board.append(piece)

        for _ in range(21):
            board.append(p.Border())

        return board

    def fen(self) -> str:
        board = ''
        empty = 0
        for row in [
            self._board[row_num * 10 : row_num * 10 + 10]
            for row_num in range(2, 10)
        ]:
            for piece in row:
                if isinstance(piece, p.Empty):
                    empty += 1
                elif isinstance(piece, p.Piece):
                    if empty != 0:
                        board += str(empty)
                        empty = 0
                    board += (
                        piece.char.upper()
                        if piece.color == WHITE
                        else piece.char
                    )
            if empty != 0:
                board += str(empty)
                empty = 0
            board += '/'
        board = board[:-1]
        active_color = 'w' if self.active_color == WHITE else 'b'
        if self.castle_rights == {
            WHITE: CastleRights(False, False),
            BLACK: CastleRights(False, False),
        }:
            castle_rights = '-'
        else:
            white_cr = self.castle_rights[WHITE]
            black_cr = self.castle_rights[BLACK]
            castle_rights = (
                'K' * white_cr.kingside
                + 'Q' * white_cr.queenside
                + 'k' * black_cr.kingside
                + 'q' * black_cr.queenside
            )
        en_passant = (
            '-' if self.en_passant == 0 else index_to_square(self.en_passant)
        )
        halfmove = str(self.halfmoves)
        fullmove = str(self.fullmoves)

        return ' '.join(
            [
                board,
                active_color,
                castle_rights,
                en_passant,
                halfmove,
                fullmove,
            ]
        )

    def _get_sets_of_pieces_by_color(self) -> dict[Color, set[p.Piece]]:
        white_pieces = set()
        black_pieces = set()
        for piece in self:
            if isinstance(piece, p.Piece):
                if piece.color == WHITE:
                    white_pieces.add(piece)
                else:
                    black_pieces.add(piece)
        return {WHITE: white_pieces, BLACK: black_pieces}

    def _get_status(self) -> status.Status:
        checked = self._is_king_in_check(self.active_color)
        has_moves = bool(self.legal_moves)
        if not has_moves:
            if checked:
                return (
                    status.Checkmate(WHITE)
                    if self.active_color == BLACK
                    else status.Checkmate(BLACK)
                )
            else:
                return status.Stalemate()
        if self.halfmoves >= 50:
            return status.Draw()
        return status.Ongoing()

    def _is_square_under_attack(
        self, index: int, color: Color | None = None
    ) -> bool:
        enemy_types = {
            type(piece)
            for piece in self._pieces[WHITE if color == BLACK else BLACK]
        }
        return any(
            Type.is_square_attacked_by_piece_type(self, index, color)
            for Type in enemy_types
        )

    def _is_king_in_check(self, color: Color):
        kings = {
            king for king in self._pieces[color] if isinstance(king, p.King)
        }
        return any(
            self._is_square_under_attack(self._board.index(king), color)
            for king in kings
        )

    def move_uci(self, move_uci: str) -> None:
        move = Move.from_uci(move_uci)
        self._move(move)

    def _move(self, move: Move) -> None:
        if move not in self.legal_moves:
            raise IllegalMoveError(f'move is not legal: {move}')

        self.halfmoves += 1
        self._total_halfmoves += 1

        if self.active_color == BLACK:
            self.fullmoves += 1

        self._move_raw(move)

        self.active_color = self._COLORS[
            self._total_halfmoves % len(self._COLORS)
        ]
        self.legal_moves = self._get_legal_moves_for_active_color()
        self.status = self._get_status()

    def _move_raw(self, move: Move, bookkepp: bool = True) -> None:
        index = move.origin
        piece = self._board[index]

        # not possible if called through Board._move
        # but possible if called directly
        # so you cannot desync the state by hitting NotAPieceError here
        # after updating Board.halfmoves and Board._total_halfmoves
        if not isinstance(piece, p.Piece):
            raise NotAPieceError(f'not a piece: {index_to_square(index)}')

        piece.make_move(self, move, bookkepp)

    @contextlib.contextmanager
    def _with_move(self, move: Move):
        board = self._board
        self._board = board.copy()
        self._move_raw(move, False)
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
