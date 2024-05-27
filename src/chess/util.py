import dataclasses
from enum import Enum, auto
from typing import NamedTuple


def square_to_index(square: str) -> int:
    col, row = square[0].lower(), square[1]
    return 20 + (ord(col) - 96) + (8 - int(row)) * 10


def index_to_square(index: int) -> str:
    row_something, col_idx = divmod(index - 20, 10)
    letter = chr(96 + col_idx)
    return f'{letter}{8 - row_something}'


class Move(NamedTuple):
    origin: int
    dest: int
    promotion: str = ''

    def __repr__(self) -> str:
        from_square = index_to_square(self.origin)
        to_square = index_to_square(self.dest)
        uci = f'{from_square}{to_square}{self.promotion}'
        return f"{self.__class__.__name__}('{uci}')"

    @classmethod
    def from_uci(cls, uci: str):
        if not 4 <= len(uci) <= 5:
            raise ValueError
        origin = square_to_index(uci[0:2])
        dest = square_to_index(uci[2:4])
        promotion = uci[4:5].upper()
        return cls(origin, dest, promotion)


@dataclasses.dataclass
class CastleRights:
    kingside: bool
    queenside: bool


class Status(Enum):
    WHITE_CHECKMATE = auto()
    BLACK_CHECKMATE = auto()
    DRAW = auto()
    STALEMATE = auto()
    ONGOING = auto()
