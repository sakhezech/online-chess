import dataclasses


@dataclasses.dataclass(unsafe_hash=True)
class Color:
    forward_sign: int
    king_row: int
    promotion_row: int
    dmove_row: int
    king_index: int
    king_rook_index: int
    queen_rook_index: int


WHITE = Color(
    forward_sign=-1,
    king_row=90,
    promotion_row=20,
    dmove_row=80,
    king_index=95,
    king_rook_index=98,
    queen_rook_index=91,
)
BLACK = Color(
    forward_sign=1,
    king_row=20,
    promotion_row=90,
    dmove_row=30,
    king_index=25,
    king_rook_index=28,
    queen_rook_index=21,
)
