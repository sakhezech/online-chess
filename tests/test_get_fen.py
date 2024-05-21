import pytest
from chess.board import Board

test_data = {
    # https://www.chessgames.com/perl/chessgame?gid=1538719
    'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1',
    'rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2',
    'rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2',
    'r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3',
    'r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3',
    'r1bqkbnr/pppp1ppp/8/1B2p3/3nP3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4',
    'r1bqkbnr/pppp1ppp/8/1B2p3/3NP3/8/PPPP1PPP/RNBQK2R b KQkq - 0 4',
    'r1bqkbnr/pppp1ppp/8/1B6/3pP3/8/PPPP1PPP/RNBQK2R w KQkq - 0 5',
    'r1bqkbnr/pppp1ppp/8/1B6/3pP3/3P4/PPP2PPP/RNBQK2R b KQkq - 0 5',
    'r1bqkbnr/pp1p1ppp/2p5/1B6/3pP3/3P4/PPP2PPP/RNBQK2R w KQkq - 0 6',
    'r1bqkbnr/pp1p1ppp/2p5/8/2BpP3/3P4/PPP2PPP/RNBQK2R b KQkq - 1 6',
    'r1bqkb1r/pp1pnppp/2p5/8/2BpP3/3P4/PPP2PPP/RNBQK2R w KQkq - 2 7',
    'r1bqkb1r/pp1pnppp/2p5/6B1/2BpP3/3P4/PPP2PPP/RN1QK2R b KQkq - 3 7',
    'r1bqkb1r/pp1pnpp1/2p4p/6B1/2BpP3/3P4/PPP2PPP/RN1QK2R w KQkq - 0 8',
    'r1bqkb1r/pp1pnpp1/2p4p/8/2BpP2B/3P4/PPP2PPP/RN1QK2R b KQkq - 1 8',
    'r1bqkb1r/pp2npp1/2p4p/3p4/2BpP2B/3P4/PPP2PPP/RN1QK2R w KQkq d6 0 9',
    'r1bqkb1r/pp2npp1/2p4p/3p4/3pP2B/1B1P4/PPP2PPP/RN1QK2R b KQkq - 1 9',
    'r2qkb1r/pp2npp1/2p1b2p/3p4/3pP2B/1B1P4/PPP2PPP/RN1QK2R w KQkq - 2 10',
    'r2qkb1r/pp2npp1/2p1b2p/3p3Q/3pP2B/1B1P4/PPP2PPP/RN2K2R b KQkq - 3 10',
    'r3kb1r/pp1qnpp1/2p1b2p/3p3Q/3pP2B/1B1P4/PPP2PPP/RN2K2R w KQkq - 4 11',
    'r3kb1r/pp1qnpp1/2p1b2p/3p4/3pP2B/1B1P4/PPP1QPPP/RN2K2R b KQkq - 5 11',
    '2kr1b1r/pp1qnpp1/2p1b2p/3p4/3pP2B/1B1P4/PPP1QPPP/RN2K2R w KQ - 6 12',
    '2kr1b1r/pp1qnpp1/2p1b2p/3p4/3pP2B/1B1P4/PPPNQPPP/R3K2R b KQ - 7 12',
    '2kr1b1r/pp1qnp2/2p1b2p/3p2p1/3pP2B/1B1P4/PPPNQPPP/R3K2R w KQ g6 0 13',
    '2kr1b1r/pp1qnp2/2p1b2p/3p2p1/3pP3/1B1P2B1/PPPNQPPP/R3K2R b KQ - 1 13',
    '2kr1b1r/pp1q1p2/2p1b1np/3p2p1/3pP3/1B1P2B1/PPPNQPPP/R3K2R w KQ - 2 14',
    '2kr1b1r/pp1q1p2/2p1b1np/3p2p1/3pP3/1B1P2B1/PPPNQPPP/2KR3R b - - 3 14',
    '2kr1b1r/pp1q4/2p1b1np/3p1pp1/3pP3/1B1P2B1/PPPNQPPP/2KR3R w - f6 0 15',
    '2kr1b1r/pp1q4/2p1b1np/3p1pp1/3pP3/1B1P1PB1/PPPNQ1PP/2KR3R b - - 0 15',
    '2kr3r/pp1q2b1/2p1b1np/3p1pp1/3pP3/1B1P1PB1/PPPNQ1PP/2KR3R w - - 1 16',
    '2kr3r/pp1q2b1/2p1b1np/3p1pp1/3pP3/1B1P1PB1/PPPNQ1PP/2KRR3 b - - 2 16',
    '2kr3r/pp1q2b1/2p1b1np/5pp1/3pp3/1B1P1PB1/PPPNQ1PP/2KRR3 w - - 0 17',
    '2kr3r/pp1q2b1/2p1b1np/5pp1/3pP3/1B3PB1/PPPNQ1PP/2KRR3 b - - 0 17',
    '2kr3r/pp1q2b1/2p1b1np/6p1/3pPp2/1B3PB1/PPPNQ1PP/2KRR3 w - - 0 18',
    '2kr3r/pp1q2b1/2p1b1np/6p1/3pPp2/1B3P2/PPPNQBPP/2KRR3 b - - 1 18',
    '2kr3r/pp1q2b1/4b1np/2p3p1/3pPp2/1B3P2/PPPNQBPP/2KRR3 w - - 0 19',
    '2kr3r/pp1q2b1/4B1np/2p3p1/3pPp2/5P2/PPPNQBPP/2KRR3 b - - 0 19',
    '2kr3r/pp4b1/4q1np/2p3p1/3pPp2/5P2/PPPNQBPP/2KRR3 w - - 0 20',
    '2kr3r/pp4b1/4q1np/2p3p1/2QpPp2/5P2/PPPN1BPP/2KRR3 b - - 1 20',
    '2kr3r/pp4b1/6np/2p3p1/2qpPp2/5P2/PPPN1BPP/2KRR3 w - - 0 21',
    '2kr3r/pp4b1/6np/2p3p1/2NpPp2/5P2/PPP2BPP/2KRR3 b - - 0 21',
    '2kr3r/p5b1/6np/1pp3p1/2NpPp2/5P2/PPP2BPP/2KRR3 w - b6 0 22',
    '2kr3r/p5b1/6np/Npp3p1/3pPp2/5P2/PPP2BPP/2KRR3 b - - 1 22',
    '2k4r/p5b1/3r2np/Npp3p1/3pPp2/5P2/PPP2BPP/2KRR3 w - - 2 23',
    '2k4r/p5b1/3r2np/1pp3p1/3pPp2/1N3P2/PPP2BPP/2KRR3 b - - 3 23',
    '2k4r/p5b1/2r3np/1pp3p1/3pPp2/1N3P2/PPP2BPP/2KRR3 w - - 4 24',
    '2k4r/p5b1/2r3np/1pp3p1/3pPp2/1N3P2/PPP2BPP/1K1RR3 b - - 5 24',
    '2kr4/p5b1/2r3np/1pp3p1/3pPp2/1N3P2/PPP2BPP/1K1RR3 w - - 6 25',
    '2kr4/p5b1/2r3np/1pp3p1/3pPp2/1NP2P2/PP3BPP/1K1RR3 b - - 0 25',
    '2kr4/p5b1/2r3np/1pp3p1/4Pp2/1Np2P2/PP3BPP/1K1RR3 w - - 0 26',
    '2kR4/p5b1/2r3np/1pp3p1/4Pp2/1Np2P2/PP3BPP/1K2R3 b - - 0 26',
    '3k4/p5b1/2r3np/1pp3p1/4Pp2/1Np2P2/PP3BPP/1K2R3 w - - 0 27',
    '3k4/p5b1/2r3np/1pp3p1/4Pp2/1Np2P2/PP3BPP/1K1R4 b - - 1 27',
    '2k5/p5b1/2r3np/1pp3p1/4Pp2/1Np2P2/PP3BPP/1K1R4 w - - 2 28',
    '2k5/p5b1/2r3np/1pB3p1/4Pp2/1Np2P2/PP4PP/1K1R4 b - - 0 28',
    '2k5/6b1/2r3np/ppB3p1/4Pp2/1Np2P2/PP4PP/1K1R4 w - a6 0 29',
    '2k5/6b1/2r3np/ppB3p1/4Pp2/1NP2P2/P5PP/1K1R4 b - - 0 29',
    '2k5/8/2r3np/ppB3p1/4Pp2/1Nb2P2/P5PP/1K1R4 w - - 0 30',
    '2k5/8/2r3np/pp4p1/4Pp2/1Nb2P2/P4BPP/1K1R4 b - - 1 30',
    '2k5/8/2r4p/pp2n1p1/4Pp2/1Nb2P2/P4BPP/1K1R4 w - - 2 31',
    '2k5/8/2r4p/pp2n1p1/3BPp2/1Nb2P2/P5PP/1K1R4 b - - 3 31',
    # https://www.chessgames.com/perl/chessgame?gid=2032754
    'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1',
    'rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2',
    'rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2',
    'r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3',
    'r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3',
    'r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4',
    'r1bqk1nr/pppp1ppp/2n5/2b1p3/1PB1P3/5N2/P1PP1PPP/RNBQK2R b KQkq b3 0 4',
    'r1bqk1nr/pppp1ppp/2n5/4p3/1bB1P3/5N2/P1PP1PPP/RNBQK2R w KQkq - 0 5',
    'r1bqk1nr/pppp1ppp/2n5/4p3/1bB1P3/2P2N2/P2P1PPP/RNBQK2R b KQkq - 0 5',
    'r1bqk1nr/pppp1ppp/2n5/b3p3/2B1P3/2P2N2/P2P1PPP/RNBQK2R w KQkq - 1 6',
    'r1bqk1nr/pppp1ppp/2n5/b3p3/2BPP3/2P2N2/P4PPP/RNBQK2R b KQkq d3 0 6',
    'r1bqk1nr/pppp1ppp/2n5/b7/2BpP3/2P2N2/P4PPP/RNBQK2R w KQkq - 0 7',
    'r1bqk1nr/pppp1ppp/2n5/b7/2BpP3/2P2N2/P4PPP/RNBQ1RK1 b kq - 1 7',
    'r1bqk1nr/pppp1ppp/1bn5/8/2BpP3/2P2N2/P4PPP/RNBQ1RK1 w kq - 2 8',
    'r1bqk1nr/pppp1ppp/1bn5/8/2BPP3/5N2/P4PPP/RNBQ1RK1 b kq - 0 8',
    'r1bqk1nr/ppp2ppp/1bnp4/8/2BPP3/5N2/P4PPP/RNBQ1RK1 w kq - 0 9',
    'r1bqk1nr/ppp2ppp/1bnp4/8/2BPP3/5N1P/P4PP1/RNBQ1RK1 b kq - 0 9',
    'r1bqk1nr/ppp2ppp/1b1p4/n7/2BPP3/5N1P/P4PP1/RNBQ1RK1 w kq - 1 10',
    'r1bqk1nr/ppp2ppp/1b1p4/n7/3PP3/3B1N1P/P4PP1/RNBQ1RK1 b kq - 2 10',
    'r1bqk1nr/pp3ppp/1b1p4/n1p5/3PP3/3B1N1P/P4PP1/RNBQ1RK1 w kq c6 0 11',
    'r1bqk1nr/pp3ppp/1b1p4/n1p5/3PP3/3B1N1P/P4PP1/RNBQR1K1 b kq - 1 11',
    'r1bqk1nr/pp3ppp/1b1p4/n7/3pP3/3B1N1P/P4PP1/RNBQR1K1 w kq - 0 12',
    'r1bqk1nr/pp3ppp/1b1p4/n7/3NP3/3B3P/P4PP1/RNBQR1K1 b kq - 0 12',
    'r1bqk1nr/pp3ppp/3p4/n7/3bP3/3B3P/P4PP1/RNBQR1K1 w kq - 0 13',
    'r1bqk1nr/pp3ppp/3p4/nB6/3bP3/7P/P4PP1/RNBQR1K1 b kq - 1 13',
    'r1bqk1nr/pp3ppp/2np4/1B6/3bP3/7P/P4PP1/RNBQR1K1 w kq - 2 14',
    'r1bqk1nr/pp3ppp/2np4/1B6/3QP3/7P/P4PP1/RNB1R1K1 b kq - 0 14',
    'r1bq1knr/pp3ppp/2np4/1B6/3QP3/7P/P4PP1/RNB1R1K1 w - - 1 15',
    'r1bq1knr/pp3ppp/2Bp4/8/3QP3/7P/P4PP1/RNB1R1K1 b - - 0 15',
    'r1bq1knr/p4ppp/2pp4/8/3QP3/7P/P4PP1/RNB1R1K1 w - - 0 16',
    'r1bq1knr/p4ppp/2pp4/8/3QP3/B6P/P4PP1/RN2R1K1 b - - 1 16',
    'r1bq1k1r/p4ppp/2pp1n2/8/3QP3/B6P/P4PP1/RN2R1K1 w - - 2 17',
    'r1bq1k1r/p4ppp/2pp1n2/4P3/3Q4/B6P/P4PP1/RN2R1K1 b - - 0 17',
    'r1bq1k1r/p4ppp/2pp4/3nP3/3Q4/B6P/P4PP1/RN2R1K1 w - - 1 18',
    'r1bq1k1r/p4ppp/2pP4/3n4/3Q4/B6P/P4PP1/RN2R1K1 b - - 0 18',
    'r2q1k1r/p2b1ppp/2pP4/3n4/3Q4/B6P/P4PP1/RN2R1K1 w - - 1 19',
    'r2q1k1r/p2bRppp/2pP4/3n4/3Q4/B6P/P4PP1/RN4K1 b - - 2 19',
    'r4k1r/p2bRppp/1qpP4/3n4/3Q4/B6P/P4PP1/RN4K1 w - - 3 20',
    'r4k1r/p2bRppp/1qpP4/2Bn4/3Q4/7P/P4PP1/RN4K1 b - - 4 20',
    'r4k1r/pq1bRppp/2pP4/2Bn4/3Q4/7P/P4PP1/RN4K1 w - - 5 21',
    'r4k1r/pq1bRppp/2pP4/2Bn4/3Q4/7P/P2N1PP1/R5K1 b - - 6 21',
    '4rk1r/pq1bRppp/2pP4/2Bn4/3Q4/7P/P2N1PP1/R5K1 w - - 7 22',
    '4Rk1r/pq1b1ppp/2pP4/2Bn4/3Q4/7P/P2N1PP1/R5K1 b - - 0 22',
    '4k2r/pq1b1ppp/2pP4/2Bn4/3Q4/7P/P2N1PP1/R5K1 w - - 0 23',
    '4k2r/pq1b1pQp/2pP4/2Bn4/8/7P/P2N1PP1/R5K1 b - - 0 23',
    '4kr2/pq1b1pQp/2pP4/2Bn4/8/7P/P2N1PP1/R5K1 w - - 1 24',
    '4kr2/pq1b1pQp/2pP4/2Bn4/8/7P/P2N1PP1/4R1K1 b - - 2 24',
    '4kr2/pq3pQp/2pPb3/2Bn4/8/7P/P2N1PP1/4R1K1 w - - 3 25',
    '4kr2/pq3pQp/2pPR3/2Bn4/8/7P/P2N1PP1/6K1 b - - 0 25',
}


@pytest.mark.parametrize('fen', test_data)
def test_get_fen(fen: str):
    board = Board(fen)
    assert board.fen == fen
