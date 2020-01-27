import random
import copy
import time

class GameError(AttributeError):
	pass

class Game:

	def __init__(self, n):
		self.size = n
		self.half_the_size = int(n/2)
		self.reset()

	def reset(self):
		self.board = []
		value = 'B'
		for i in range(self.size):
			row = []
			for j in range(self.size):
				row.append(value)
				value = self.opponent(value)
			self.board.append(row)
			if self.size%2 == 0:
				value = self.opponent(value)

	def __str__(self):
		result = "  "
		for i in range(self.size):
			result += str(i) + " "
		result += "\n"
		for i in range(self.size):
			result += str(i) + " "
			for j in range(self.size):
				result += str(self.board[i][j]) + " "
			result += "\n"
		return result

	def valid(self, row, col):
		return row >= 0 and col >= 0 and row < self.size and col < self.size

	def contains(self, board, row, col, symbol):
		return self.valid(row,col) and board[row][col]==symbol

	def countSymbol(self, board, symbol):
		count = 0
		for r in range(self.size):
			for c in range(self.size):
				if board[r][c] == symbol:
					count += 1
		return count

	def opponent(self, player):
		if player == 'B':
			return 'W'
		else:
			return 'B'

	def distance(self, r1, c1, r2, c2):
		return abs(r1-r2 + c1-c2)

	def makeMove(self, player, move):
		self.board = self.nextBoard(self.board, player, move)

	def nextBoard(self, board, player, move):
		r1 = move[0]
		c1 = move[1]
		r2 = move[2]
		c2 = move[3]
		next = copy.deepcopy(board)
		if not (self.valid(r1, c1) and self.valid(r2, c2)):
			raise GameError
		if next[r1][c1] != player:
			raise GameError
		dist = self.distance(r1, c1, r2, c2)
		if dist == 0:
			if self.openingMove(board):
				next[r1][c1] = "."
				return next
			raise GameError
		if next[r2][c2] != ".":
			raise GameError
		jumps = int(dist/2)
		dr = int((r2 - r1)/dist)
		dc = int((c2 - c1)/dist)
		for i in range(jumps):
			if next[r1+dr][c1+dc] != self.opponent(player):
				raise GameError
			next[r1][c1] = "."
			next[r1+dr][c1+dc] = "."
			r1 += 2*dr
			c1 += 2*dc
			next[r1][c1] = player
		return next

	def openingMove(self, board):
		return self.countSymbol(board, ".") <= 1

	def generateFirstMoves(self, board):
		moves = []
		moves.append([0]*4)
		moves.append([self.size-1]*4)
		moves.append([self.half_the_size]*4)
		moves.append([(self.half_the_size)-1]*4)
		return moves

	def generateSecondMoves(self, board):
		moves = []
		if board[0][0] == ".":
			moves.append([0,1]*2)
			moves.append([1,0]*2)
			return moves
		elif board[self.size-1][self.size-1] == ".":
			moves.append([self.size-1,self.size-2]*2)
			moves.append([self.size-2,self.size-1]*2)
			return moves
		elif board[self.half_the_size-1][self.half_the_size-1] == ".":
			pos = self.half_the_size -1
		else:
			pos = self.half_the_size
		moves.append([pos,pos-1]*2)
		moves.append([pos+1,pos]*2)
		moves.append([pos,pos+1]*2)
		moves.append([pos-1,pos]*2)
		return moves

	def check(self, board, r, c, rd, cd, factor, opponent):
		if self.contains(board,r+factor*rd,c+factor*cd,opponent) and \
		   self.contains(board,r+(factor+1)*rd,c+(factor+1)*cd,'.'):
			return [[r,c,r+(factor+1)*rd,c+(factor+1)*cd]] + \
				   self.check(board,r,c,rd,cd,factor+2,opponent)
		else:
			return []

	def generateMoves(self, board, player):
		if self.openingMove(board):
			if player=='B':
				return self.generateFirstMoves(board)
			else:
				return self.generateSecondMoves(board)
		else:
			moves = []
			rd = [-1,0,1,0]
			cd = [0,1,0,-1]
			for r in range(self.size):
				for c in range(self.size):
					if board[r][c] == player:
						for i in range(len(rd)):
							moves += self.check(board,r,c,rd[i],cd[i],1,
												self.opponent(player))
			return moves

	def playOneGame(self, p1, p2, show):
		self.reset()
		while True:
			if show:
				print(self)
				print("player B's turn")
			move = p1.getMove(self.board)
			if move == []:
				if show:
					print("Game over")
				return 'W'
			try:
				self.makeMove('B', move)
			except GameError:
				print("Game over: Invalid move by", p1.name)
				print(move)
				print(self)
				return 'W'
			if show:
				print(move)
				print(self)
				print("player W's turn")
			move = p2.getMove(self.board)
			if move == []:
				if show:
					print("Game over")
				return 'B'
			try:
				self.makeMove('W', move)
			except GameError:
				print("Game over: Invalid move by", p2.name)
				print(move)
				print(self)
				return 'B'
			if show:
				print(move)

	def playNGames(self, n, p1, p2, show):
		first = p1
		second = p2
		for i in range(n):
			if show:
				print("Game", i)
			winner = self.playOneGame(first, second, show)
			if winner == 'B':
				first.won()
				second.lost()
				if show:
					print(first.name, "wins")
			else:
				first.lost()
				second.won()
				if show:
					print(second.name, "wins")
			# first, second = second, first


class Player:
	name = "Player"
	wins = 0
	losses = 0
	def results(self):
		result = self.name
		result += " Wins:" + str(self.wins)
		result += " Losses:" + str(self.losses)
		return result
	def lost(self):
		self.losses += 1
	def won(self):
		self.wins += 1
	def reset(self):
		self.wins = 0
		self.losses = 0

	def initialize(self, side):
		abstract()

	def getMove(self, board):
		abstract()


class SimplePlayer(Game, Player):
	def initialize(self, side , depth):
		self.side = side
		self.name = "Simple"
	def getMove(self, board):
		moves = self.generateMoves(board, self.side)
		n = len(moves)
		if n == 0:
			return []
		else:
			return moves[0]

class RandomPlayer(Game, Player):
	def initialize(self, side , depth):
		self.side = side
		self.name = "Random"
	def getMove(self, board):
		moves = self.generateMoves(board, self.side)
		n = len(moves)
		if n == 0:
			return []
		else:
			return moves[random.randrange(0, n)]

class HumanPlayer(Game, Player):
	def initialize(self, side , depth):
		self.side = side
		self.name = "Human"
	def getMove(self, board):
		moves = self.generateMoves(board, self.side)
		while True:
			print("Possible moves:", moves)
			n = len(moves)
			if n == 0:
				print("You must concede")
				return []
			index = input("Enter index of chosen move (0-"+ str(n-1) +
						  ") or -1 to concede: ")
			try:
				index = int(index)
				if index == -1:
					return []
				if 0 <= index <= (n-1):
					print("returning", moves[index])
					return moves[index]
				else:
					print("Invalid choice, try again.")
			except Exception as e:
				print("Invalid choice, try again.")

UTIL_WIN = 1
UTIL_LOSE = -1
ROOT_DEPTH = 0

class MinimaxPlayer(Game, Player):
	def initialize(self, side , depth):
		self.side = side
		self.name = "minimax"
		self.depth = depth 

	def getMove(self, board):
		value , move = self.max_value(board , self.side , ROOT_DEPTH)
		return move

	def min_value(self , board , side , depth):
		# terminal condition
		if self.utility(board , side) is not None:
			return self.utility(board , side) , None
		# depth condition
		if depth == self.depth :
			return self.eval_func(board , side) , None
		# init node value and corresponding action
		v = float('inf')
		m = None
		# for each successor 
		moves = self.generateMoves(board , side)
		for move in moves : 
			new_v , new_m = self.max_value(self.nextBoard(board , side , move) 
				, self.opponent(side) , depth + 1)
			if new_v < v :
				v = new_v
				m = move
			if new_v == v:
				if(random.randrange(2) == 1):
					v = new_v
					m = move
					
		# return node value and corresponding action
		return v , m
	
	
	def max_value(self , board , side , depth):
		# terminal condition
		if self.utility(board , side) is not None:
			return self.utility(board , side) , []
		# depth condition
		if depth == self.depth :
			return self.eval_func(board , side) , None
		# init node value and corresponding action
		v = float('-inf')
		m = None
		# for each successor 
		moves = self.generateMoves(board , side)
		for move in moves : 
			new_v , new_m =self.min_value(self.nextBoard(board , side , move) 
				, self.opponent(side) , depth + 1)
			if new_v > v :
				v = new_v
				m = move
			if new_v == v:
				if(random.randrange(2) == 1):
					v = new_v
					m = move
					
		# return node value and corresponding action
		return v , m
	
	
	def utility(self , board , side):
		moves = self.generateMoves(board, side)
		if len(moves):
			return None
		if side == self.side:
			return UTIL_LOSE
		return UTIL_WIN
	
	def eval_func(self , board , side):
		my = len(self.generateMoves(board ,self.side))
		opponent = len(self.generateMoves(board , self.opponent(self.side)))
		return (UTIL_WIN * my + UTIL_LOSE*opponent)/(my + opponent)
					
class PrunerPlayer(MinimaxPlayer):
	def initialize(self, side , depth):
		self.side = side
		self.name = "pruner"
		self.depth = depth 

	def getMove(self, board):
		value , move = self.max_value(board , self.side , ROOT_DEPTH , 
		float('-inf') , float('inf'))
		return move
			
	def min_value(self , board , side , depth , a , b):
		# terminal condition
		if self.utility(board , side) is not None:
			return self.utility(board , side) , None
		# depth condition
		if depth == self.depth :
			return self.eval_func(board , side) , None
		# init node value and corresponding action
		v = float('inf')
		m = None
		# for each successor 
		moves = self.generateMoves(board , side)
		for move in moves : 
			new_v , new_m = self.max_value(self.nextBoard(board , side , move) 
				, self.opponent(side) , depth + 1 , a , b)
			if new_v < v :
				v = new_v
				m = move
			if new_v == v:
				if(random.randrange(2) == 1):
					v = new_v
					m = move
			if v <= a :
				return v , m
			b = min(b , v)
					
		# return node value and corresponding action
		return v , m

	def max_value(self , board , side , depth , a , b):
		# terminal condition
		if self.utility(board , side) is not None:
			return self.utility(board , side) , []
		# depth condition
		if depth == self.depth :
			return self.eval_func(board , side) , None
		# init node value and corresponding action
		v = float('-inf')
		m = None
		# for each successor 
		moves = self.generateMoves(board , side)
		for move in moves : 
			new_v , new_m =self.min_value(self.nextBoard(board , side , move) 
				, self.opponent(side) , depth + 1 , a , b)
			if new_v > v :
				v = new_v
				m = move
			if new_v == v:
				if(random.randrange(2) == 1):
					v = new_v
					m = move
			if v >= b :
				return v , m
			a = max(a , v)
					
		# return node value and corresponding action
		return v , m

def stat(game , p1 , p2 , n):
	# resetn players
	start = time.time()
	game.playNGames(n , p1 , p2 , False)
	end = time.time()
	return [(end - start)/n , p1.wins/n]
	
def stats(min_dim , max_dim ,min_depth ,  max_depth , n , player):
	'''
	min_dim >= 3
	min_depth >= 1
	'''

	data = []
	for i in range(min_dim , max_dim+1):
		data.append([])
		for j in range(min_depth , max_depth+1):
			data[i - min_dim].append([])
	for i in range(min_dim , max_dim+1):
		for j in range( min_depth , max_depth+1):
			dim = i
			depth = j
			game = Game(dim)
			p1 = player(dim)
			p2 = player(dim)
			p1.initialize('B' , depth)
			p2.initialize('W' , depth)
			data[i-min_dim][j-min_depth] = stat(game , p1 , p2 , n)
	return data

if __name__ == '__main__':
	dim = 8
	n = 20
	game = Game(dim)
	p1 = PrunerPlayer(dim)
	p1.initialize('B' , 4)
	p2 = PrunerPlayer(dim)
	p2.initialize('W' , 1)
	game.playNGames(n , p1 , p2 , True)
	print(p1.wins/n)