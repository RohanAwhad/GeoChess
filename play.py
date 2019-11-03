#!/usr/bin/env python3
from flask import Flask, Response, request
import time
from train import Net
import torch
import chess
import traceback
import chess.svg
from state import State

class Valuator(object):
    def __init__(self):
        self.model = Net()
        vals = torch.load("nets/value.pth", map_location=lambda storage, loc: storage)
        self.model.load_state_dict(vals)

    def __call__(self, s):
        brd = s.serialize()[None]
        output = self.model(torch.tensor(brd).float())
        return float(output.data[0][0])

def explore_leaves(s, v):
    ret = []
    temp = s.board
    for e in s.edges():
        s.board.push(e)
        ret.append((v(s), e))
        s.board.pop()
    assert temp == s.board
    return ret

#Chess Board and Engine
v = Valuator()
s = State()

def computer_move():
    move = sorted(explore_leaves(s, v), key=lambda x: x[0], reverse=s.board.turn)[0]
    print(move)
    s.board.push(move[1])

app = Flask(__name__)
@app.route('/')
def hello():
    ret = '<html>'
    ret += '<head>'
    ret += '<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>'
    ret += '<style>input{font-size:24px; }button {font-size:24px; }</style>'
    ret += '</head>'
    ret += '<body>'
    ret += '<img width=500, height=500 src="/board.svg?%f"></img><br>' % time.time()
    ret += '<form action="/human"><input type="text" name="move"><input type="submit" value="Move"></form><br>'
    #ret += '<button onclick=\'$.ajax({type: "POST", url:"/move", success: function rf(){ location.reload();}});\'>Make Computer Move</button>'
    ret += '</body>'
    ret += '</html>'
    return ret

@app.route('/board.svg')
def board():
    # play vs human
    return Response(chess.svg.board(board=s.board), mimetype='image/svg+xml')

@app.route('/human')
def human_move():
    if not s.board.is_game_over():
        move = request.args.get('move', default="")
        if move is not None and move != '':
            print(f'Human moves {move}')
            try:
                s.board.push_san(move)
                computer_move()
            except Exception:
                traceback.print_exc()
    else:
        print('GAME IS OVER')
    return hello()

@app.route('/move', methods=['POST'])
def comp_move():
    computer_move()
    return ''

if __name__ == '__main__':
    app.run(debug=True)


'''
if __name__ == '__main__':

    #self play
    while not s.board.is_game_over():
        l = sorted(explore_leaves(s, v), key=lambda x: x[0], reverse=s.board.turn)
        move = l[0]
        print(move)
        s.board.push(move[1])
    print(s.board.result())
    
'''       
