import pytest
from chess.util import index_to_square, square_to_index

cols = {
    'a': 1,
    'b': 2,
    'c': 3,
    'd': 4,
    'e': 5,
    'f': 6,
    'g': 7,
    'h': 8,
}
rows = {
    '8': 20,
    '7': 30,
    '6': 40,
    '5': 50,
    '4': 60,
    '3': 70,
    '2': 80,
    '1': 90,
}

square_to_index_data = {
    col_char + row_char: col_val + row_val
    for col_char, col_val in cols.items()
    for row_char, row_val in rows.items()
}
index_to_square_data = {v: k for k, v in square_to_index_data.items()}
incorrect_square_data = {'-', 'a0', 'b11', 'c9' 'hello', '12', 'ab', 'x7'}
incorrect_index_data = {-1, 0, 15, 20, 29, 30, 99, 105, 307, 502}


@pytest.mark.parametrize('square, index', square_to_index_data.items())
def test_square_to_index(square: str, index: int):
    assert square_to_index(square) == index


@pytest.mark.parametrize('index, square', index_to_square_data.items())
def test_index_to_square(index: int, square: str):
    assert index_to_square(index) == square


@pytest.mark.parametrize('square', incorrect_square_data)
def test_incorrect_square(square: str):
    with pytest.raises(ValueError):
        square_to_index(square)


@pytest.mark.parametrize('index', incorrect_index_data)
def test_incorrect_index(index: int):
    with pytest.raises(ValueError):
        index_to_square(index)
