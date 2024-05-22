import copy

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
        new_board.active_color = not board.active_color
        new_board._move(move)
        res = get_number_of_moves(new_board, depth - 1)
        sum += res
    return sum


perft_results = {
    1: 20,
    2: 400,
    3: 8_902,
    4: 197_281,
    5: 4_865_609,
    6: 119_060_324,
    7: 3_195_901_860,
}


def test_perft(perft_depth: int):
    board = Board()
    assert (
        get_number_of_moves(board, perft_depth) == perft_results[perft_depth]
    )
