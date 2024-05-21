from chess.board import Board
from chess.pieces import Piece


def get_number_of_moves(board: Board, depth: int, to_move: bool = True):
    legal = set()
    for i, piece in enumerate(board._board):
        if isinstance(piece, Piece) and piece.color == to_move:
            legal.update(board._get_legal_moves_by_index(i))
    if depth == 1:
        return len(legal)

    sum = 0
    for move in legal:
        new_board = Board()
        new_board._board = board._board.copy()
        new_board.en_passant = board.en_passant
        new_board.castle_rights = board.castle_rights
        new_board._pieces = board._pieces
        with new_board.with_move(move):
            res = get_number_of_moves(new_board, depth - 1, not to_move)
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
