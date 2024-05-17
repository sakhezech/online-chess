import chess.pieces as p
import pytest
from chess.board import Board
from chess.util import index_to_square

test_data = {
    'kP4N1/4bb2/8/8/1pPpp2R/1K1P1Q2/P7/5P2 w - - 0 1': {
        p.Pawn: {'e4', 'd3', 'f3'},
        p.Knight: {'e7'},
        p.Bishop: {'h4', 'c4', 'g8'},
        p.Rook: {'e4'},
        p.Queen: {'e4', 'f7'},
        p.King: {'b4', 'b8'},
    },
}


@pytest.mark.parametrize(
    'data',
    [
        (fen, Type, expected)
        for fen, type_and_expected in test_data.items()
        for Type, expected in type_and_expected.items()
    ],
)
def test_threat_check(data):
    fen, Type, expected = data
    board = Board(fen)
    threats = {
        index_to_square(index)
        for index, _ in enumerate(board._board)
        if Type.threatens_index(index, board)
    }
    assert threats == expected
