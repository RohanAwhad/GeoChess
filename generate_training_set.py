#!/usr/bin/env python3

import os
import chess.pgn
from state import State
import numpy as np


def get_dataset(num_samples=None):
    #pgn files in data/pgns folder
    X = []
    Y = []
    gn = 0
    values = {'1/2-1/2':0, '0-1':-1, '1-0':1}
    for fn in os.listdir('data/pgns'):
        pgn = open(os.path.join("data/pgns", fn))
        while 1:
            try:
                game = chess.pgn.read_game(pgn)
            except Exception as e:
                break
            res = game.headers['Result']
            if res not in values:
                continue
            value = values[res]
            board = game.board()
            for i, move in enumerate(game.mainline_moves()):
                board.push(move)
                # TODO: extract the board moves
                ser = State(board).serialize()
                X.append(ser)
                Y.append(value)
            print(f'Parsing game {gn}, got {len(X)} examples')
            gn += 1
            if num_samples is not None and len(X) > num_samples:
                return X, Y

    X = np.array(X)
    Y = np.array(Y)
    return X, Y


if __name__ == "__main__":
    X, Y = get_dataset(1e7)
    np.savez("processed/dataset_10M.npz", X, Y)
