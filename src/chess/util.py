import dataclasses
from typing import NamedTuple


def square_to_index(square: str) -> int:
    if len(square) != 2:
        raise ValueError(f'not a square: {square}')
    col, row = ord(square[0].lower()), int(square[1])
    if not 1 <= row <= 8:
        raise ValueError('row is not between 1 and 8: {square[1]}')
    if not 97 <= col <= 105:
        raise ValueError(f'column is not between a and h: {square[0].lower()}')
    return 20 + (col - 96) + (8 - row) * 10


def index_to_square(index: int) -> str:
    if not 21 <= index <= 98 or index % 10 in {0, 9}:
        raise ValueError(f'index not on board: {index}')
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
