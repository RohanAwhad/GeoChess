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
				  chess.KING: 100 }

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
		

def computer_minimax(s, v, alpha, beta, depth=2):
	if depth == 0 or s.board.is_game_over():
		return v(s)
	else:
		turn = s.board.turn
		if turn == chess.WHITE: ret = -MAXVAL
		else: ret = MAXVAL
		for e in s.edges():
			#print(f'Pre Ret: {ret}, White Play: {s.board.turn}')
			s.board.push(e)
			tval = computer_minimax(s, v, alpha, beta, depth-1)
			if turn == chess.WHITE:
				ret = max(ret, tval)
				alpha = max(alpha, tval)
			else:
				ret = min(ret, tval)
				beta = min(beta, tval)
			#print(f'Post Ret: {ret}, tVal: {tval}, White Play: {s.board.turn}')
			s.board.pop()
			if beta <= alpha: break
		return ret

def explore_leaves(s, v):
	ret = []
	print(s.edges()[0])
	for e in s.edges():
		s.board.push(e)
		ret.append((computer_minimax(s, v, -100000, 100000), e))
		s.board.pop()
	return ret

#Chess Board and Engine
v = Valuator()
#v = ClassicValuator()
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
	ret = open('index.html').read()
	return ret

@app.route('/board.svg')
def board():
	# play vs human
	return Response(chess.svg.board(board=s.board), mimetype='image/svg+xml')

@app.route('/move')
def move():
	if not s.board.is_game_over():
		move = request.args.get('move', default="")
		if move is not None and move != '':
			print(f'Human moves {move}')
			try:
				s.board.push_san(move)
				computer_move(s, v)
			except Exception:
				traceback.print_exc()
			response = app.response_class(
				response=s.board.fen(),
				status=200
			)
			return response
	else:
		print('GAME IS OVER')
		response = app.response_class(
			response="Game Over",
			status=200
		)
		return response
	return hello()

@app.route("/move_coordinates")
def move_coordinates():
	if not s.board.is_game_over():
		source = int(request.args.get('from', default=''))
		target = int(request.args.get('to', default=''))
		promotion = True if request.args.get('promotion', default='') == 'true' else False

		move = s.board.san(chess.Move(source, target, promotion=chess.QUEEN if promotion else None))

		if move is not None and move != "":
			print("Human Moves", move)
			try:
				s.board.push_san(move)
				computer_move(s,v)
			except Exception:
				traceback.print_exc()
			response=app.response_class(
				response=s.board.fen(),
				status=200
			)

			return response

	print('GAME IS OVER')
	response = app.response_class(
		response="Game Over",
		status=200
	)
	return response

@app.route("/newgame")
def newgame():
	s.board.reset()
	print('GAME IS OVER')
	response = app.response_class(
		response=s.board.fen(),
		status=200
	)
	return response

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
