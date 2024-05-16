def pytest_addoption(parser):
    parser.addoption(
        '--perft-depth',
        type=int,
        default=1,
        help='list of stringinputs to pass to test functions',
    )


def pytest_generate_tests(metafunc):
    if 'perft_depth' in metafunc.fixturenames:
        metafunc.parametrize(
            'perft_depth', [metafunc.config.getoption('perft_depth')]
        )
