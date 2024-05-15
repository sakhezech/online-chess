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

    @classmethod
    def threatens_index(
        cls,
        index: int,
        board: list['Piece | Empty | Border'],
    ):
        raise NotImplementedError

    def make_move(
        self,
        move: Move,
        board: list['Piece | Empty | Border'],
        castle_rights: CastleRights,
    ) -> tuple[int, CastleRights]:
        board[move.origin] = Empty()
        board[move.dest] = self
        return 0, castle_rights

    @property
    def icon(self) -> str:
        return self.char.upper() if self.color else self.char


class SymmetricMovePiece(Piece):
    @classmethod
    def threatens_index(
        cls,
        index: int,
        board: list['Piece | Empty | Border'],
    ):
        target = board[index]
        if not isinstance(target, Piece):
            return False
        target_color = target.color
        fake_piece = cls(target_color)
        cr = CastleRights.from_bools(False, False, False, False)
        moves = fake_piece.get_pseudolegal_moves(board, 0, cr, index)
        for move in moves:
            piece = board[move.dest]
            if isinstance(piece, cls):
                return True
        return False


class SlidingPiece(SymmetricMovePiece):
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


class JumpingPiece(SymmetricMovePiece):
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

    @classmethod
    def threatens_index(
        cls,
        index: int,
        board: list['Piece | Empty | Border'],
    ) -> bool:
        target = board[index]
        if not isinstance(target, Piece):
            return False
        target_color = target.color
        offsets = {-9, -11} if target_color else {9, 11}
        for offset in offsets:
            piece = board[index + offset]
            if isinstance(piece, cls) and piece.color != target_color:
                return True
        return False

    def make_move(
        self,
        move: Move,
        board: list['Piece | Empty | Border'],
        castle_rights: CastleRights,
    ) -> tuple[int, CastleRights]:
        super().make_move(move, board, castle_rights)
        if abs(move.origin - move.dest) == 20:
            idx = (move.origin + move.dest) // 2
        else:
            idx = 0
        return idx, castle_rights


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
        move: Move,
        board: list['Piece | Empty | Border'],
        castle_rights: CastleRights,
    ) -> tuple[int, CastleRights]:
        super().make_move(move, board, castle_rights)
        king_row = 90 if self.color else 20
        cr = castle_rights.white if self.color else castle_rights.black

        kingside = (king_row + 8 != move.origin) and cr.kingside
        queenside = (king_row + 1 != move.origin) and cr.queenside
        if self.color:
            new_rights = castle_rights.with_white(kingside, queenside)
        else:
            new_rights = castle_rights.with_black(kingside, queenside)
        return 0, new_rights


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

    def make_move(
        self,
        move: Move,
        board: list['Piece | Empty | Border'],
        castle_rights: CastleRights,
    ) -> tuple[int, CastleRights]:
        king_row = 90 if self.color else 20
        king_index = king_row + 5
        kingside_castle_index = king_row + 7
        queenside_castle_index = king_row + 3
        if self.color:
            new_rights = castle_rights.with_white(False, False)
        else:
            new_rights = castle_rights.with_black(False, False)
        if move.origin == king_index:
            if move.dest == kingside_castle_index:
                board[move.origin] = Empty()
                board[king_row + 7] = self
                board[king_row + 6] = board[king_row + 8]
                board[king_row + 8] = Empty()
                return 0, new_rights
            elif move.dest == queenside_castle_index:
                board[move.origin] = Empty()
                board[king_row + 3] = self
                board[king_row + 4] = board[king_row + 1]
                board[king_row + 1] = Empty()
                return 0, new_rights

        return super().make_move(move, board, castle_rights)


class Empty(BoardEntity):
    char = '.'


class Border(BoardEntity):
    pass
