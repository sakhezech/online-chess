from .move import Move


class Piece:
    char = ''

    def __init__(self, color: bool = True) -> None:
        self.color = color

    @property
    def icon(self) -> str:
        return self.char.upper() if self.color else self.char

    def get_pseudolegal_moves(
        self,
        board: list['Piece'],
        en_passant_idx: int,
        index: int | None = None,
    ) -> set[Move]:
        raise NotImplementedError


class SlidingPiece(Piece):
    offsets: list[int]

    def get_pseudolegal_moves(
        self,
        board: list[Piece],
        en_passant_idx: int,
        index: int | None = None,
    ) -> set[Move]:
        moves = set()
        if index is None:
            index = board.index(self)
        for offset in self.offsets:
            offsetted_index = index
            while True:
                offsetted_index += offset
                piece = board[offsetted_index]
                ptype = type(piece)

                if ptype is Empty:
                    moves.add(Move(index, offsetted_index))
                elif ptype is Border:
                    break
                elif piece.color != self.color:
                    moves.add(Move(index, offsetted_index))
                    break
                else:  # piece.color == self.color
                    break
        return moves


class NonSlidingPiece(Piece):
    offsets: list[int]

    def get_pseudolegal_moves(
        self,
        board: list[Piece],
        en_passant_idx: int,
        index: int | None = None,
    ) -> set[Move]:
        moves = set()
        if index is None:
            index = board.index(self)
        for offset in self.offsets:
            offsetted_index = index + offset
            piece = board[offsetted_index]
            ptype = type(piece)

            if ptype is not Border and (
                ptype is Empty or piece.color != self.color
            ):
                moves.add(Move(index, offsetted_index))
        return moves


class Pawn(Piece):
    char = 'p'

    def get_pseudolegal_moves(
        self,
        board: list[Piece],
        en_passant_idx: int,
        index: int | None = None,
    ) -> set[Move]:
        # TODO: pawn movement
        return set()


class Knight(NonSlidingPiece):
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


class King(NonSlidingPiece):
    char = 'k'
    offsets = [-11, -10, -9, -1, 1, 9, 10, 11]

    def get_pseudolegal_moves(
        self,
        board: list[Piece],
        en_passant_idx: int,
        index: int | None = None,
    ) -> set[Move]:
        moves = super().get_pseudolegal_moves(board, en_passant_idx, index)
        # TODO: castling
        return moves


class Empty(Piece):
    char = '.'


class Border(Piece):
    pass
