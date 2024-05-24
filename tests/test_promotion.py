import pytest
from chess.board import Board
from chess.color import BLACK, WHITE
from chess.pieces import Bishop, Knight, Piece, Queen, Rook
from chess.util import CastleRights, Move, square_to_index

test_data = [
    ('a7a8P', Queen),
    ('b7b8N', Knight),
    ('c7c8B', Bishop),
    ('d7d8R', Rook),
    ('e7e8Q', Queen),
    ('f7f8K', Queen),
    ('g7g8', Queen),
    ('h7h8A', Queen),
]


@pytest.mark.parametrize('move, expected', test_data)
def test_promotion(move: str, expected: Piece):
    board = Board('8/PPPPPPPP/8/8/8/8/8/8 w - - 0 1')
    move_ = Move.from_uci(move)
    board._move(move_)
    assert board[move_.dest].__class__ == expected


def make_castle_rights(K: bool, Q: bool, k: bool, q: bool):
    return {WHITE: CastleRights(K, Q), BLACK: CastleRights(k, q)}


test_data = [
    (['a1b1', 'b1a1'], make_castle_rights(True, False, True, True)),
    (['h1f1', 'f1h1'], make_castle_rights(False, True, True, True)),
    (['e1d1', 'd1e1'], make_castle_rights(False, False, True, True)),
    (['a8b8', 'b8a8'], make_castle_rights(True, True, True, False)),
    (['h8f8', 'f8h8'], make_castle_rights(True, True, False, True)),
    (['e8d8', 'd8e8'], make_castle_rights(True, True, False, False)),
]


@pytest.mark.parametrize('moves, expected', test_data)
def test_castle_rights(moves: list[str], expected: dict[str, CastleRights]):
    board = Board('r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1')
    for move in moves:
        board._move(Move.from_uci(move))
    assert board.castle_rights == expected


def test_en_passant_index():
    board = Board()
    board._move(Move.from_uci('a2a4'))
    assert board.en_passant == square_to_index('a3')
    board._move(Move.from_uci('a4a5'))
    assert board.en_passant == 0
    board._move(Move.from_uci('h7h5'))
    assert board.en_passant == square_to_index('h6')
    board._move(Move.from_uci('h5h4'))
    assert board.en_passant == 0
