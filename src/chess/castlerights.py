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

    def with_white(self, kingside: bool, queenside: bool):
        return self.__class__(SideRights(kingside, queenside), self.black)

    def with_black(self, kingside: bool, queenside: bool):
        return self.__class__(self.white, SideRights(kingside, queenside))
