def square_to_index(square: str) -> int:
    col, row = square[0].lower(), square[1]
    return 20 + (ord(col) - 96) + (8 - int(row)) * 10


def index_to_square(index: int) -> str:
    row_something, col_idx = divmod(index - 20, 10)
    letter = chr(96 + col_idx)
    return f'{letter}{8 - row_something}'
