#!/usr/bin/env python3

import os
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

MAXVAL = 10000
class ClassicValuator(object):

	def __init__(self):
		self.values = {chess.PAWN: 1,
				  chess.KNIGHT: 3, 
				  chess.BISHOP: 3,
				  chess.ROOK: 5,
				  chess.QUEEN: 9,
				  chess.KING: 0 }

	def __call__(self, s):
		if s.board.is_variant_win():
			if s.board.turn == chess.WHITE: return MAXVAL
			else: return -MAXVAL
		if s.board.is_variant_loss():
			if s.board.turn == chess.WHITE: return -MAXVAL
			else: return MAXVAL
			
		pm = s.board.piece_map()
		val = 0
		for x in pm:
			if pm[x].color == chess.WHITE:
				val += self.values[pm[x].piece_type]
			else:
				val -= self.values[pm[x].piece_type]
		return val
		

def computer_minimax(s, v, depth=2):
	if depth == 0 or s.board.is_game_over():
		return v(s)
	else:
		turn = s.board.turn
		if turn == chess.WHITE: ret = -MAXVAL
		else: ret = MAXVAL
		for e in s.edges():
			#print(f'Pre Ret: {ret}, White Play: {s.board.turn}')
			s.board.push(e)
			tval = computer_minimax(s, v, depth-1)
			if turn == chess.WHITE:
				ret = max(ret, tval)
			else:
				ret = min(ret, tval)
			#print(f'Post Ret: {ret}, tVal: {tval}, White Play: {s.board.turn}')
			s.board.pop()
		return ret

def explore_leaves(s, v):
	ret = []
	temp = s.board
	for e in s.edges():
		s.board.push(e)
		ret.append((computer_minimax(s, v), e))
		#exit(0)
		s.board.pop()
	assert temp == s.board
	return ret

#Chess Board and Engine
#v = Valuator()
v = ClassicValuator()
s = State()



def computer_move(s, v):
	move = sorted(explore_leaves(s, v), key=lambda x: x[0], reverse=s.board.turn)
	print('TOP 3: ')
	for i, m in enumerate(move[:3]):
		print('\t',m)
	s.board.push(move[0][1])

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
				computer_move(s, v)
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
	if os.getenv("SELFPLAY") is not None:
		s = State()
		while not s.board.is_game_over():
			print(s.board)
			computer_move(s, v)
		print(s.board.result)
	else: 
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
