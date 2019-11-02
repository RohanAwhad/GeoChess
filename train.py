#!/usr/bin/env python3

import os
import chess.pgn
from state import State

for fn in os.listdir('data/pgns'):
    pgn = open(os.path.join("data/pgns", fn))
    while 1:
        game = chess.pgn.read_game(pgn)
        value = {'1/2-1/2':0, '0-1':-1, '1-0':1}[game.headers['Result']]
        board = game.board()
        for i, move in enumerate(game.mainline_moves()):
            board.push(move)
            # TODO: extract the board moves
            print(value, State(board).serialize())
    break
