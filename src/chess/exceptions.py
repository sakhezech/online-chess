class ChessError(Exception):
    pass


class FENError(ChessError):
    pass


class NotAPieceError(ChessError):
    pass


class IllegalMoveError(ChessError):
    pass
