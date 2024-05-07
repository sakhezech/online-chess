from typing import NamedTuple

from .util import index_to_square, square_to_index


class Move(NamedTuple):
    from_idx: int
    to_idx: int
    promotion: str = ''

    def __repr__(self) -> str:
        from_square = index_to_square(self.from_idx)
        to_square = index_to_square(self.to_idx)
        sttr = f'{from_square}{to_square}{self.promotion}'
        return f"{self.__class__.__name__}('{sttr}')"

    @classmethod
    def from_uci(cls, uci: str):
        if not 4 <= len(uci) <= 5:
            raise ValueError
        from_idx = square_to_index(uci[0:2])
        to_idx = square_to_index(uci[2:4])
        promotion = uci[4]
        return cls(from_idx, to_idx, promotion)
