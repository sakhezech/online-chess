import pytest
from chess.board import Board
from chess.move import Move
from chess.pieces import Bishop, Knight, Piece, Queen, Rook

test_data = {
    'a7a8P': Queen,
    'b7b8N': Knight,
    'c7c8B': Bishop,
    'd7d8R': Rook,
    'e7e8Q': Queen,
    'f7f8K': Queen,
    'g7g8': Queen,
    'h7h8A': Queen,
}


@pytest.mark.parametrize('move, expected', test_data.items())
def test_promotion(move: str, expected: Piece):
    board = Board('8/PPPPPPPP/8/8/8/8/8/8 w - - 0 1')
    move_ = Move.from_uci(move)
    board._move(move_)
    assert board[move_.dest].__class__ == expected
