import copy

import pytest
from chess.board import Board
from chess.pieces import Piece


def get_number_of_moves(board: Board, depth: int):
    legal = set()
    for i, piece in enumerate(board._board):
        if isinstance(piece, Piece) and piece.color == board.active_color:
            legal.update(board._get_legal_moves_by_index(i))
    if depth == 1:
        return len(legal)

    sum = 0
    for move in legal:
        new_board = copy.deepcopy(board)
        new_board._COLORS = board._COLORS
        new_board._total_halfmoves += 1
        new_board.active_color = new_board._COLORS[
            new_board._total_halfmoves % len(new_board._COLORS)
        ]
        new_board._move_raw(move)
        res = get_number_of_moves(new_board, depth - 1)
        sum += res
    return sum


# https://www.chessprogramming.org/Perft_Results


@pytest.mark.perft
def test_perft():
    board = Board()
    assert get_number_of_moves(board, 4) == 197281


@pytest.mark.perft
def test_another_perft2():
    board = Board(
        'r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1'
    )
    assert get_number_of_moves(board, 3) == 97862


@pytest.mark.perft
def test_another_perft3():
    board = Board('8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1')
    assert get_number_of_moves(board, 4) == 43238


@pytest.mark.perft
def test_another_perft4():
    board = Board(
        'r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1'
    )
    assert get_number_of_moves(board, 3) == 9467


@pytest.mark.perft
def test_another_perft5():
    board = Board('rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8')
    assert get_number_of_moves(board, 3) == 62379


@pytest.mark.perft
def test_another_perft6():
    board = Board(
        'r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1'
        ' w - - 0 10'
    )
    assert get_number_of_moves(board, 3) == 89890
