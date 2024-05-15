from typing import NamedTuple


class SideRights(NamedTuple):
    kingside: bool
    queenside: bool


class CastleRights(NamedTuple):
    white: SideRights
    black: SideRights

    @classmethod
    def from_bools(cls, K: bool, Q: bool, k: bool, q: bool):
        return cls(SideRights(K, Q), SideRights(k, q))
