#!/usr/bin/env python3

import os
import chess.pgn
from state import State

def get_dataset(num_samples=None):
    #pgn files in data/pgns folder
    X = []
    Y = []
    gn = 0
    for fn in os.listdir('data/pgns'):
        pgn = open(os.path.join("data/pgns", fn))
        while 1:
            game = chess.pgn.read_game(pgn)
            value = {'1/2-1/2':0, '0-1':-1, '1-0':1}[game.headers['Result']]
            board = game.board()
            for i, move in enumerate(game.mainline_moves()):
                board.push(move)
                # TODO: extract the board moves
                ser = State(board).serialize()[:, :, 0]
                X.append(ser)
                Y.append(value)
            print(f'Parsing game {gn}, got {len(X)} examples')
            gn += 1
            if num_samples is not None and len(X) > num_samples:
                return X, Y

    return X, Y


if __name__ == "__main__":
    X, Y = get_dataset(1000)
