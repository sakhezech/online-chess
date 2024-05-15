from .castlerights import CastleRights
from .move import Move


class BoardEntity:
    char = ''

    @property
    def icon(self) -> str:
        return self.char


class Piece(BoardEntity):
    def __init__(self, color: bool = True) -> None:
        self.color = color

    def get_pseudolegal_moves(
        self,
        board: list['Piece | Empty | Border'],
        en_passant: int,
        castle_rights: CastleRights,
        index: int | None = None,
    ) -> set[Move]:
        raise NotImplementedError

    @property
    def icon(self) -> str:
        return self.char.upper() if self.color else self.char


class SlidingPiece(Piece):
    offsets: list[int]

    def get_pseudolegal_moves(
        self,
        board: list['Piece | Empty | Border'],
        en_passant: int,
        castle_rights: CastleRights,
        index: int | None = None,
    ) -> set[Move]:
        moves = set()
        if index is None:
            index = board.index(self)
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


class JumpingPiece(Piece):
    offsets: list[int]

    def get_pseudolegal_moves(
        self,
        board: list['Piece | Empty | Border'],
        en_passant: int,
        castle_rights: CastleRights,
        index: int | None = None,
    ) -> set[Move]:
        moves = set()
        if index is None:
            index = board.index(self)
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

    def get_pseudolegal_moves(
        self,
        board: list['Piece | Empty | Border'],
        en_passant: int,
        castle_rights: CastleRights,
        index: int | None = None,
    ) -> set[Move]:
        moves = set()
        if index is None:
            index = board.index(self)
        double_move_row = 80 if self.color else 30
        offset = -10 if self.color else 10
        attack_offsets = {offset + 1, offset - 1}

        target_index = index + offset
        piece = board[target_index]
        if isinstance(piece, Empty):
            moves.add(Move(index, target_index))
            target_index += offset
            piece = board[target_index]
            if double_move_row <= index <= double_move_row + 10 and isinstance(
                piece, Empty
            ):
                moves.add(Move(index, target_index))

        for attack_offset in attack_offsets:
            target_index = index + attack_offset
            piece = board[target_index]
            en_passant_piece = board[en_passant - offset]
            if (
                target_index == en_passant
                and isinstance(en_passant_piece, Pawn)
                and en_passant_piece.color != self.color
                or isinstance(piece, Piece)
                and piece.color != self.color
            ):
                moves.add(Move(index, target_index))

        return moves


class Knight(JumpingPiece):
    char = 'n'
    offsets = [-21, -19, -12, -8, 8, 12, 19, 21]


class Bishop(SlidingPiece):
    char = 'b'
    offsets = [-11, -9, 9, 11]


class Rook(SlidingPiece):
    char = 'r'
    offsets = [-10, -1, 1, 10]


class Queen(SlidingPiece):
    char = 'q'
    offsets = [-11, -10, -9, -1, 1, 9, 10, 11]


class King(JumpingPiece):
    char = 'k'
    offsets = [-11, -10, -9, -1, 1, 9, 10, 11]

    def get_pseudolegal_moves(
        self,
        board: list['Piece | Empty | Border'],
        en_passant: int,
        castle_rights: CastleRights,
        index: int | None = None,
    ) -> set[Move]:
        moves = super().get_pseudolegal_moves(
            board, en_passant, castle_rights, index
        )
        if index is None:
            index = board.index(self)

        king_row = 90 if self.color else 20
        king_index = king_row + 5
        queenside = {4, 3, 2}
        kingside = {6, 7}
        cr = castle_rights.white if self.color else castle_rights.black

        if index != king_index:
            return moves

        if cr.queenside and all(
            isinstance(board[i + king_row], Empty) for i in queenside
        ):
            moves.add(Move(index, king_row + 3))
        if cr.kingside and all(
            isinstance(board[i + king_row], Empty) for i in kingside
        ):
            moves.add(Move(index, king_row + 7))
        return moves


class Empty(BoardEntity):
    char = '.'


class Border(BoardEntity):
    pass
