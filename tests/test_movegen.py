import pytest
from chess.board import Board
from chess.move import Move


def make_expected(origin: str, dests: list[str]) -> set[Move]:
    return {Move.from_uci(f'{origin}{dest}') for dest in dests}


test_data: dict[str, dict[str, list[str]]] = {
    # KNIGHT
    '8/8/2N5/8/3p4/6N1/8/N6N w KQkq - 0 1': {
        'a1': ['b3', 'c2'],
        'h1': ['f2'],
        'c6': ['a7', 'b8', 'd8', 'e7', 'e5', 'd4', 'b4', 'a5'],
    },
    # BISHOP
    '8/1B6/5p2/8/3B4/8/8/B7 w KQkq - 0 1': {
        'a1': ['b2', 'c3'],
        'd4': ['b2', 'c3', 'e5', 'f6', 'c5', 'b6', 'a7', 'e3', 'f2', 'g1'],
        'b7': ['a8', 'a6', 'c8', 'c6', 'd5', 'e4', 'f3', 'g2', 'h1'],
    },
    # ROOK
    '8/8/5p2/8/8/2p2R1p/8/2R1Rp1R w KQkq - 0 1': {
        'c1': ['a1', 'b1', 'd1', 'c2', 'c3'],
        'e1': ['d1', 'f1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8'],
        'h1': ['g1', 'f1', 'h2', 'h3'],
        'f3': ['e3', 'd3', 'c3', 'g3', 'h3', 'f2', 'f1', 'f4', 'f5', 'f6'],
    },
    # QUEEN
    '5ppp/5PQp/5ppp/p7/3P4/8/8/Q4P2 w KQkq - 0 1': {
        'a1': ['a2', 'a3', 'a4', 'a5', 'b2', 'c3', 'b1', 'c1', 'd1', 'e1'],
        'g7': ['f8', 'g8', 'h8', 'h7', 'f6', 'g6', 'h6'],
    },
    # KING
    'rnb1kbnr/pppppppp/8/8/8/3PP3/PPPq1PPP/R3K1NR w KQkq - 0 1': {
        'e1': ['c1', 'd1', 'd2', 'e2', 'f1'],
    },
    'rnb1kbnr/pppppppp/8/8/8/3PPP2/PPP3PP/R3K2R w Kkq - 0 1': {
        'e1': ['d1', 'd2', 'e2', 'f1', 'f2', 'g1'],
    },
    'r3k2r/pppp1ppp/8/4p3/8/8/PPPPPPPP/R3K2R b q - 0 1': {
        'e8': ['f8', 'e7', 'd8', 'c8']
    },
    # PAWN
    '5P2/8/8/8/2PpPp2/7p/Pq1PP2P/2P5 b - e3 0 1': {
        'a2': ['a3', 'a4'],
        'c1': ['c2', 'b2'],
        'd2': ['d3'],
        'e4': ['e5'],
        'd4': ['d3', 'e3'],
        'f8': [],
        'h2': [],
        'h3': [],
    },
    '8/p2p1ppp/1p2p1P1/PPp5/8/8/8/8 w KQkq c6 0 1': {
        'a7': ['a6'],
        'b6': ['a5'],
        'c5': ['c4'],
        'd7': ['d6', 'd5'],
        'e6': ['e5'],
        'f7': ['f6', 'f5', 'g6'],
        'g7': [],
        'h7': ['h6', 'h5', 'g6'],
        'a5': ['a6', 'b6'],
        'b5': ['c6'],
    },
}

TestData = tuple[str, str, list[str]]


# @pytest.mark.parametrize('data', test_data)
@pytest.mark.parametrize(
    'data',
    [
        (fen, square, dests)
        for fen, from_and_tos in test_data.items()
        for square, dests in from_and_tos.items()
    ],
)
def test_piece_movegen(data: TestData):
    fen, square, dests = data
    board = Board(fen)
    moves = board._get_pseudolegal_moves_by_square(square)
    expected = make_expected(square, dests)
    assert moves == expected
