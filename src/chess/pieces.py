from typing import TYPE_CHECKING

from .color import WHITE, Color
from .exceptions import NotAPieceError
from .util import Move, index_to_square

if TYPE_CHECKING:
    from .board import Board


class BoardEntity:
    char = ''

    @property
    def icon(self) -> str:
        return self.char


class Piece(BoardEntity):
    def __init__(self, color: Color) -> None:
        self.color = color

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.color.name}')"

    def get_pseudolegal_moves(self, board: 'Board', index: int) -> set[Move]:
        raise NotImplementedError

    def get_legal_moves(self, board: 'Board', index: int) -> set[Move]:
        pseudolegal_moves = self.get_pseudolegal_moves(board, index)
        legal_moves = set()
        for move in pseudolegal_moves:
            with board._with_move(move):
                if not board._is_king_in_check(self.color):
                    legal_moves.add(move)
        return legal_moves

    @classmethod
    def is_square_attacked_by_piece_type(
        cls,
        board: 'Board',
        index: int,
        color: Color | None = None,
    ) -> bool:
        raise NotImplementedError

    def make_move(
        self,
        board: 'Board',
        move: Move,
        bookkeep: bool = True,
    ) -> None:
        if bookkeep:
            captured_piece = board[move.dest]
            if isinstance(captured_piece, Piece):
                board.halfmoves = 0
                board._pieces[captured_piece.color].remove(captured_piece)
                cr = board.castle_rights[captured_piece.color]
                if move.dest == captured_piece.color.king_rook_index:
                    cr.kingside = False
                if move.dest == captured_piece.color.queen_rook_index:
                    cr.queenside = False
            board.en_passant = 0

        board[move.origin] = Empty()
        board[move.dest] = self

    @property
    def icon(self) -> str:
        # TODO: make color agnostic
        return self.char.upper() if self.color == WHITE else self.char


class SymmetricMovePiece(Piece):
    @classmethod
    def is_square_attacked_by_piece_type(
        cls,
        board: 'Board',
        index: int,
        color: Color | None = None,
    ) -> bool:
        target = board[index]
        if color is not None:
            target_color = color
        else:
            if not isinstance(target, Piece):
                return False
            target_color = target.color
        fake_piece = cls(target_color)
        moves = fake_piece.get_pseudolegal_moves(board, index)
        for move in moves:
            piece = board[move.dest]
            if isinstance(piece, cls):
                return True
        return False


class SlidingPiece(SymmetricMovePiece):
    offsets: list[int]

    def get_pseudolegal_moves(self, board: 'Board', index: int) -> set[Move]:
        moves = set()
        for offset in self.offsets:
            target_index = index
            while True:
                target_index += offset
                piece = board[target_index]

                if isinstance(piece, Empty):
                    moves.add(Move(index, target_index))
                elif isinstance(piece, Border):
                    break
                elif piece.color != self.color:
                    moves.add(Move(index, target_index))
                    break
                else:  # piece.color == self.color
                    break
        return moves


class JumpingPiece(SymmetricMovePiece):
    offsets: list[int]

    def get_pseudolegal_moves(self, board: 'Board', index: int) -> set[Move]:
        moves = set()
        for offset in self.offsets:
            target_index = index + offset
            piece = board[target_index]

            if isinstance(piece, Border):
                continue
            if isinstance(piece, Empty) or piece.color != self.color:
                moves.add(Move(index, target_index))

        return moves


class Pawn(Piece):
    char = 'p'

    def _make_moves(self, board: 'Board', origin: int, dest: int) -> set[Move]:
        if self.color.promotion_row <= dest <= self.color.promotion_row + 10:
            return {
                Move(origin, dest, Type.char.upper())
                for Type in board._PAWN_PROMOTIONS
            }
        return {Move(origin, dest)}

    def get_pseudolegal_moves(self, board: 'Board', index: int) -> set[Move]:
        moves = set()
        offset = 10 * self.color.forward_sign
        attack_offsets = {offset + 1, offset - 1}

        target_index = index + offset
        piece = board[target_index]
        if isinstance(piece, Empty):
            moves.update(self._make_moves(board, index, target_index))
            target_index += offset
            piece = board[target_index]
            if (
                self.color.dmove_row <= index <= self.color.dmove_row + 10
                and isinstance(piece, Empty)
            ):
                moves.update(self._make_moves(board, index, target_index))

        for attack_offset in attack_offsets:
            target_index = index + attack_offset
            piece = board[target_index]
            en_passant_piece = board[board.en_passant - offset]
            if (
                target_index == board.en_passant
                and isinstance(en_passant_piece, Pawn)
                and en_passant_piece.color != self.color
                or isinstance(piece, Piece)
                and piece.color != self.color
            ):
                moves.update(self._make_moves(board, index, target_index))

        return moves

    @classmethod
    def is_square_attacked_by_piece_type(
        cls,
        board: 'Board',
        index: int,
        color: Color | None = None,
    ) -> bool:
        if color is not None:
            target_color = color
        else:
            target = board[index]
            if not isinstance(target, Piece):
                return False
            target_color = target.color
        offsets = {
            9 * target_color.forward_sign,
            11 * target_color.forward_sign,
        }
        for offset in offsets:
            piece = board[index + offset]
            if isinstance(piece, cls) and piece.color != target_color:
                return True
        return False

    def make_move(
        self,
        board: 'Board',
        move: Move,
        bookkeep: bool = True,
    ) -> None:
        if move.dest == board.en_passant:
            en_passanted_index = (
                board.en_passant - 10 * self.color.forward_sign
            )
            if bookkeep:
                en_passanted = board[en_passanted_index]
                if not isinstance(en_passanted, Piece):
                    raise NotAPieceError(
                        "no piece en passant'ed:"
                        f' {index_to_square(en_passanted_index)}'
                    )
                board._pieces[en_passanted.color].remove(en_passanted)
            board[en_passanted_index] = Empty()

        super().make_move(board, move, bookkeep)
        Type = None
        if (
            self.color.promotion_row
            <= move.dest
            <= self.color.promotion_row + 10
        ):
            Type = board._CHAR_TO_PROMOTION[move.promotion.lower()]

        if bookkeep:
            if move.origin - move.dest == -20 * self.color.forward_sign:
                idx = (move.origin + move.dest) // 2
            else:
                idx = 0
            board.en_passant = idx
            board.halfmoves = 0
            if Type:
                new_piece = Type(self.color)
                board[move.dest] = new_piece
                board._pieces[self.color].remove(self)
                board._pieces[self.color].add(new_piece)


class Knight(JumpingPiece):
    char = 'n'
    offsets = [-21, -19, -12, -8, 8, 12, 19, 21]


class Bishop(SlidingPiece):
    char = 'b'
    offsets = [-11, -9, 9, 11]


class Rook(SlidingPiece):
    char = 'r'
    offsets = [-10, -1, 1, 10]

    def make_move(
        self,
        board: 'Board',
        move: Move,
        bookkeep: bool = True,
    ) -> None:
        super().make_move(board, move, bookkeep)

        if bookkeep:
            cr = board.castle_rights[self.color]

            cr.kingside = cr.kingside and (
                self.color.king_rook_index != move.origin
            )
            cr.queenside = cr.queenside and (
                self.color.queen_rook_index != move.origin
            )


class Queen(SlidingPiece):
    char = 'q'
    offsets = [-11, -10, -9, -1, 1, 9, 10, 11]


class King(JumpingPiece):
    char = 'k'
    offsets = [-11, -10, -9, -1, 1, 9, 10, 11]

    def get_legal_moves(self, board: 'Board', index: int) -> set[Move]:
        legal_moves = super().get_legal_moves(board, index)
        kingside = Move(self.color.king_index, self.color.king_index + 2)
        queenside = Move(self.color.king_index, self.color.king_index - 2)

        if board._is_square_under_attack(self.color.king_index, self.color):
            try:
                legal_moves.remove(queenside)
            except KeyError:
                pass
            try:
                legal_moves.remove(kingside)
            except KeyError:
                pass

        if board._is_square_under_attack(
            self.color.king_index - 1, self.color
        ):
            try:
                legal_moves.remove(queenside)
            except KeyError:
                pass
        if board._is_square_under_attack(
            self.color.king_index + 1, self.color
        ):
            try:
                legal_moves.remove(kingside)
            except KeyError:
                pass
        return legal_moves

    def get_pseudolegal_moves(self, board: 'Board', index: int) -> set[Move]:
        moves = super().get_pseudolegal_moves(board, index)

        cr = board.castle_rights[self.color]

        if index != self.color.king_index:
            return moves

        if cr.queenside and all(
            isinstance(board[i], Empty)
            for i in range(
                self.color.queen_rook_index + 1, self.color.king_index
            )
        ):
            moves.add(Move(index, self.color.king_index - 2))
        if cr.kingside and all(
            isinstance(board[i], Empty)
            for i in range(
                self.color.king_index + 1, self.color.king_rook_index
            )
        ):
            moves.add(Move(index, self.color.king_index + 2))
        return moves

    def make_move(
        self,
        board: 'Board',
        move: Move,
        bookkeep: bool = True,
    ) -> None:
        super().make_move(board, move, bookkeep)

        if move.origin == self.color.king_index:
            if move.dest == self.color.king_index + 2:
                board[self.color.king_index + 1] = board[
                    self.color.king_rook_index
                ]
                board[self.color.king_rook_index] = Empty()
            elif move.dest == self.color.king_index - 2:
                board[self.color.king_index - 1] = board[
                    self.color.queen_rook_index
                ]
                board[self.color.queen_rook_index] = Empty()

        if bookkeep:
            cr = board.castle_rights[self.color]
            cr.kingside = False
            cr.queenside = False


class Empty(BoardEntity):
    char = '.'


class Border(BoardEntity):
    pass
