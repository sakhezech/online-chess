from .move import Move


class Piece:
    char = ''

    def __init__(self, color: bool = True) -> None:
        self.color = color

    @property
    def icon(self) -> str:
        raise NotImplementedError

    def get_pseudolegal_moves(
        self,
        board: list['Piece'],
        en_passant_idx: int,
        index: int | None = None,
    ) -> list[Move]:
        raise NotImplementedError


class SlidingPiece(Piece):
    offsets: list[int]

    def get_pseudolegal_moves(
        self, board: list[Piece], en_passant_idx: int, index: int | None = None
    ) -> list[Move]:
        moves = []
        if index is None:
            index = board.index(self)
        for offset in self.offsets:
            offsetted_index = index
            while True:
                offsetted_index += offset
                piece = board[offsetted_index]
                ptype = type(piece)

                if ptype is Empty:
                    moves.append(Move(index, offsetted_index))
                elif ptype is Border:
                    break
                elif piece.color != self.color:
                    moves.append(Move(index, offsetted_index))
                    break
                else:  # piece.color == self.color
                    break
        return moves


class NonSlidingPiece(Piece):
    offsets: list[int]

    def get_pseudolegal_moves(
        self, board: list[Piece], en_passant_idx: int, index: int | None = None
    ) -> list[Move]:
        moves = []
        if index is None:
            index = board.index(self)
        for offset in self.offsets:
            offsetted_index = index + offset
            piece = board[offsetted_index]
            ptype = type(piece)

            if ptype is not Border and (
                ptype is Empty or piece.color != self.color
            ):
                moves.append(Move(index, offsetted_index))
        return moves


class Pawn(Piece):
    char = 'p'

    @property
    def icon(self) -> str:
        return 'P' if self.color else 'p'

    def get_pseudolegal_moves(
        self, board: list[Piece], en_passant_idx: int, index: int | None = None
    ) -> list[Move]:
        # TODO: pawn movement
        return []


class Knight(NonSlidingPiece):
    char = 'n'
    offsets = [-21, -19, -12, -8, 8, 12, 19, 21]

    @property
    def icon(self) -> str:
        return 'N' if self.color else 'n'


class Bishop(SlidingPiece):
    char = 'b'
    offsets = [-11, -9, 9, 11]

    @property
    def icon(self) -> str:
        return 'B' if self.color else 'b'


class Rook(SlidingPiece):
    char = 'r'
    offsets = [-10, -1, 1, 10]

    @property
    def icon(self) -> str:
        return 'R' if self.color else 'r'


class Queen(SlidingPiece):
    char = 'q'
    offsets = [-11, -10, -9, -1, 1, 9, 10, 11]

    @property
    def icon(self) -> str:
        return 'Q' if self.color else 'q'


class King(NonSlidingPiece):
    char = 'k'
    offsets = [-11, -10, -9, -1, 1, 9, 10, 11]

    @property
    def icon(self) -> str:
        return 'K' if self.color else 'k'

    def get_pseudolegal_moves(
        self, board: list[Piece], en_passant_idx: int, index: int | None = None
    ) -> list[Move]:
        moves = super().get_pseudolegal_moves(board, en_passant_idx, index)
        # TODO: castling
        return moves


class Empty(Piece):
    @property
    def icon(self) -> str:
        return '.'


class Border(Piece):
    pass
