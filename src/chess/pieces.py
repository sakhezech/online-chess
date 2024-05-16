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
        self.forward_sign = -1 if color else 1
        self.king_row = 90 if color else 20
        self.dmove_row = 80 if color else 30
        self.king_index = self.king_row + 5
        self.king_rook_index = self.king_row + 8
        self.queen_rook_index = self.king_row + 1

    def get_pseudolegal_moves(
        self,
        board: list['Piece | Empty | Border'],
        en_passant: int,
        castle_rights: CastleRights,
        index: int,
    ) -> set[Move]:
        raise NotImplementedError

    def get_legal_moves(
        self,
        board: list['Piece | Empty | Border'],
        en_passant: int,
        castle_rights: CastleRights,
        index: int,
    ) -> set[Move]:
        pseudolegal_moves = self.get_pseudolegal_moves(
            board,
            en_passant,
            castle_rights,
            index,
        )
        king = [
            king
            for king in board
            if isinstance(king, King) and king.color == self.color
        ][0]
        enemy_types = {
            type(piece) for piece in board if isinstance(piece, Piece)
        }
        legal_moves = set()
        for move in pseudolegal_moves:
            board_copy = board.copy()
            piece = board_copy[move.origin]
            if not isinstance(piece, Piece):
                raise ValueError
            piece.make_move(move, board_copy, castle_rights)
            king_index = board_copy.index(king)
            if any(
                Type.threatens_index(king_index, board_copy)
                for Type in enemy_types
            ):
                continue
            legal_moves.add(move)
        return legal_moves

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
        index: int,
    ) -> set[Move]:
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

    def get_pseudolegal_moves(
        self,
        board: list['Piece | Empty | Border'],
        en_passant: int,
        castle_rights: CastleRights,
        index: int,
    ) -> set[Move]:
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

    def get_pseudolegal_moves(
        self,
        board: list['Piece | Empty | Border'],
        en_passant: int,
        castle_rights: CastleRights,
        index: int,
    ) -> set[Move]:
        moves = set()
        offset = 10 * self.forward_sign
        attack_offsets = {offset + 1, offset - 1}

        target_index = index + offset
        piece = board[target_index]
        if isinstance(piece, Empty):
            moves.add(Move(index, target_index))
            target_index += offset
            piece = board[target_index]
            if self.dmove_row <= index <= self.dmove_row + 10 and isinstance(
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
        offsets = {9 * target.forward_sign, 11 * target.forward_sign}
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
        if move.origin - move.dest == -20 * self.forward_sign:
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
        cr = castle_rights.white if self.color else castle_rights.black

        kingside = (self.king_rook_index != move.origin) and cr.kingside
        queenside = (self.queen_rook_index + 1 != move.origin) and cr.queenside
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
        index: int,
    ) -> set[Move]:
        moves = super().get_pseudolegal_moves(
            board, en_passant, castle_rights, index
        )

        cr = castle_rights.white if self.color else castle_rights.black

        if index != self.king_index:
            return moves

        if cr.queenside and all(
            isinstance(board[i], Empty)
            for i in range(self.queen_rook_index + 1, self.king_index)
        ):
            moves.add(Move(index, self.queen_rook_index + 2))
        if cr.kingside and all(
            isinstance(board[i], Empty)
            for i in range(self.king_index + 1, self.king_rook_index)
        ):
            moves.add(Move(index, self.king_rook_index - 1))
        return moves

    def make_move(
        self,
        move: Move,
        board: list['Piece | Empty | Border'],
        castle_rights: CastleRights,
    ) -> tuple[int, CastleRights]:
        if self.color:
            new_rights = castle_rights.with_white(False, False)
        else:
            new_rights = castle_rights.with_black(False, False)

        if move.origin == self.king_index:
            if move.dest == self.queen_rook_index - 1:
                board[move.origin] = Empty()
                board[self.queen_rook_index - 1] = self
                board[self.queen_rook_index - 2] = board[self.queen_rook_index]
                board[self.queen_rook_index] = Empty()
                return 0, new_rights
            elif move.dest == self.king_rook_index + 2:
                board[move.origin] = Empty()
                board[self.king_rook_index + 2] = self
                board[self.king_rook_index + 3] = board[self.king_rook_index]
                board[self.king_rook_index] = Empty()
                return 0, new_rights

        return super().make_move(move, board, new_rights)


class Empty(BoardEntity):
    char = '.'


class Border(BoardEntity):
    pass
