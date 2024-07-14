from chess.board import Board
from chess.color import BLACK, WHITE
from chess.status import Checkmate
from chess.util import CastleRights


def test_full_game():
    board = Board()
    moves = [
        'e2e4',
        'd7d5',
        'e4d5',
        'd8d5',
        'b1c3',
        'd5d8',
        'f1c4',
        'g8f6',
        'g1f3',
        'c8g4',
        'h2h3',
        'g4f3',
        'd1f3',
        'e7e6',
        'f3b7',
        'b8d7',
        'c3b5',
        'a8c8',
        'b5a7',
        'd7b6',
        'a7c8',
        'b6c8',
        'd2d4',
        'c8d6',
        'c4b5',
        'd6b5',
        'b7b5',
        'f6d7',
        'd4d5',
        'e6d5',
        'c1e3',
        'f8d6',
        'a1d1',
        'd8f6',
        'd1d5',
        'f6g6',
        'e3f4',
        'd6f4',
        'b5d7',
        'e8f8',
        'd7d8',
    ]
    for move in moves:
        board.move_uci(move)
    # 3Q1k1r/2p2ppp/6q1/3R4/5b2/7P/PPP2PP1/4K2R b K - 2 21
    assert board.status == Checkmate(WHITE)
    assert board.halfmoves == 2
    assert board.fullmoves == 21
    assert board.en_passant == 0
    assert board.castle_rights == {
        WHITE: CastleRights(True, False),
        BLACK: CastleRights(False, False),
    }
