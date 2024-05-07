from typing import NamedTuple

from .util import index_to_square, square_to_index


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
        promotion = uci[4]
        return cls(origin, dest, promotion)
