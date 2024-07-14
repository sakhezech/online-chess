from .color import Color


class Status:
    def __eq__(self, value: object, /) -> bool:
        return (
            isinstance(value, type(self)) and self.__dict__ == value.__dict__
        )


class Checkmate(Status):
    def __init__(self, winner: Color) -> None:
        super().__init__()
        self.winner = winner


class Draw(Status):
    pass


class Stalemate(Status):
    pass


class Ongoing(Status):
    pass
