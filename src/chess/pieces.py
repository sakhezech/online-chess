class Piece:
    char = ''

    def __init__(self, color: bool = True) -> None:
        self.color = color

    @property
    def icon(self) -> str:
        raise NotImplementedError


class Pawn(Piece):
    char = 'p'

    @property
    def icon(self) -> str:
        return 'P' if self.color else 'p'


class Knight(Piece):
    char = 'n'

    @property
    def icon(self) -> str:
        return 'N' if self.color else 'n'


class Bishop(Piece):
    char = 'b'

    @property
    def icon(self) -> str:
        return 'B' if self.color else 'b'


class Rook(Piece):
    char = 'r'

    @property
    def icon(self) -> str:
        return 'R' if self.color else 'r'


class Queen(Piece):
    char = 'q'

    @property
    def icon(self) -> str:
        return 'Q' if self.color else 'q'


class King(Piece):
    char = 'k'

    @property
    def icon(self) -> str:
        return 'K' if self.color else 'k'


class Empty(Piece):
    @property
    def icon(self) -> str:
        return '.'


class Border(Piece):
    pass
