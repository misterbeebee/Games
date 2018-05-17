#!/bin/env python
import random
import sys
import time

def printf(*args):
   sys.stdout.write(*args)
   sys.stdout.flush()

class Column:
  SPACE = ' '
  def __init__(s, height):
    s.height=height
    # Bottom-to-top (aka order of insertion, per gravity)
    s.content = [s.SPACE]*s.height

  def full(s):
   return not (s[s.height-1] == s.SPACE)

  def insert(s, token):
    for rowi in range(s.height):
      if (s[rowi] == s.SPACE) and (rowi == 0 or (not s[rowi-1] == s.SPACE)):
        s[rowi] = token
        return True
    return False

  def remove(s):
    for rowi in range(s.height):
      if (not s[rowi] == s.SPACE) and (rowi == (len(s)-1) or (s[rowi+1] == s.SPACE)):
        s[rowi] = s.SPACE
        return True
    return False

  def __len__(s): return len(s.content)
  def __iter__(s): return iter(s.content)
  def __getitem__(s, i): return s.content[i]
  def __setitem__(s, i, value): s.content[i] = value
   
class Board:
  WIN_SIZE = 4
  WIDTH = 7
  HEIGHT = 6
  SPACE = ' '
  
  def __init__(s, tokens):
    s.cols = [Column(s.HEIGHT) for i in range(s.WIDTH)]
    s.tokens = tokens

  def full(s): return all([col.full() for col in s.cols])
  def insert(s, colname, token): return s.cols[colname].insert(token)
  def remove(s, colname): return s.cols[colname].remove()
      
  def winner(s):
    for coli in range(s.WIDTH):
      for rowi in range(s.HEIGHT):
        token = s.cols[coli][rowi]
        offsets = range(s.WIN_SIZE)
        # Scans everything twice, but OK
        for token in s.tokens:
          # horizontal
          h = all([(coli + offset < s.WIDTH) and (token == s.cols[coli+offset][rowi]) for offset in offsets])
          # vertical
          v = all([(rowi + offset < s.HEIGHT) and (token == s.cols[coli][rowi + offset]) for offset in offsets])
          # diagonal
          d1 = all([(coli + offset < s.WIDTH) and (rowi + offset < s.HEIGHT)
                   and (token == s.cols[coli + offset][rowi + offset]) for offset in offsets])           
          d2 = all([(coli + offset < s.WIDTH) and (rowi - offset > 0)
                    and (token == s.cols[coli + offset][rowi - offset]) for offset in offsets])           
          winner = h or v or d2
          if winner:
            return token
    return winner

  def legal_move(s, coli): return not s.cols[coli].full()
  def legal_moves(s): return [coli for coli in range(len(s.cols)) if s.legal_move(coli)]

  def print(s):
    printf('\n')
    for rowi in range(s.HEIGHT-1, -1, -1):
      printf('|')
      labels = [s.cols[coli][rowi] for coli in range(s.WIDTH)]
      printf(' '.join(labels))
      printf('|\n')
    printf('+%s+\n' % '-'.join(('-' * s.WIDTH)))
    printf(' %s \n' % ' '.join([str(i) for i in range(s.WIDTH)]))

class Player():
  def __init__(s, name, token):
    s.name = name
    s.token = token
    # Caller must call setup() next!
    
  def setup(s, game, board):
    s.game = game
    s.board = board


def indexof(array, value):
  for i in range(len(array)):
    if array[i] == value:
       return i
  return None
    
class AI(Player):
  def __init__(s, token):
    Player.__init__(s, name="Marvin", token=token) 

  def move(s):
    # Win or avoid immediate loss if possible
    tokeni = indexof(s.game.tokens, s.token)
    # my moves:
    winning_moves = set()
    losing_moves = set()
    this_token = s.game.tokens[tokeni]
    for colname in s.board.legal_moves():
      s.board.insert(colname, this_token)
      if s.board.winner():
        winning_moves.add(colname)
        # don't break, need to undo insert
      else:
        next_token = s.game.tokens[(tokeni + 1) % len(s.game.tokens)]
        opponent_winning_move = None
        for next_colname in s.board.legal_moves():
          s.board.insert(next_colname, next_token)
          if s.board.winner():
            losing_moves.add(colname)
            # don't break, need to undo insert
          s.board.remove(next_colname)
      s.board.remove(colname)

    # opponent moves:
    blocking_moves = set()
    sacrificial_moves = set()
    tokeni = (tokeni + 1) % len(s.game.tokens)
    this_token = s.game.tokens[tokeni]
    for colname in s.board.legal_moves():
      s.board.insert(colname, this_token)
      if s.board.winner():
        # Prevent opponent win.
        blocking_moves.add(colname)
        # don't break, need to undo insert
      else:
        next_token = s.game.tokens[(tokeni + 1) % len(s.game.tokens)]
        next_winning_move = None
        for next_colname in s.board.legal_moves():
          s.board.insert(next_colname, next_token)
          if s.board.winner():
            sacrificial_moves.add(next_colname)
            # don't break, need to undo insert
          s.board.remove(next_colname)
      s.board.remove(colname)
      
    if winning_moves:
      #printf("Winning move.\n")
      return list(winning_moves)[0]
    if blocking_moves:
      #printf("Blocking move.\n")
      return list(blocking_moves)[0]
    legal_moves = s.board.legal_moves()
    #print("sacrificial:", sacrificial_moves)
    #print("losing: ", losing_moves)
    #print("legal: ", legal_moves)
    # not-bad moves, or else a move that might let opponent block, or else any move (surrender)
    possible_moves = ([move for move in legal_moves
                       if (move not in losing_moves)
                       and (move not in sacrificial_moves)]
                      or list(sacrificial_moves) or legal_moves)
    
    # random move
    #printf("Random move.\n")
    start_movei = int(random.random() * len(possible_moves))
    for move_i in possible_moves:
      move = possible_moves[(start_movei + move_i) % len(possible_moves)]
      if s.board.legal_move(move):
        return move
    raise Exception("Can't move!")

class User(Player):
  def __init__(s, name, token):
    Player.__init__(s, name, token)

  def move(s):
   try:
     return int(sys.stdin.readline()[0])
   except:
     return None 
   
class Game:
  X = 'X'
  O = 'O'

  def __init__(s, tokens, players, board):
    s.tokens = tokens
    s.players = players
    s.board = board
    s.turni = int(len(s.players)*random.random())
    for player in s.players:
      player.setup(game=s, board=board) 
 
  def over(s):
    return (s.board.full(), s.board.winner())
  
  def play(s):
    s.board.print()
    while True:
      s.playturn()
      (full, winner_token) = s.over()
      if winner_token or full:
        printf('\n GAME OVER. ')
        if winner_token:
           printf('%s wins!\n\n' % winner_token)
        else:
           printf('Draw.')
        return
      # time.sleep(1)

  def playturn(s):
    player = s.players[s.turni]
    printf("\n%s %s's turn.  Move (column #): \n" % (player.token, player.name))
    s.turni = (s.turni+1) % len(s.players)
    while True:
      colname = player.move()
      printf("Move: Column %s\n" % colname)
      try:
        if s.board.insert(colname, player.token):
         break
      except: pass
      printf('ILLEGAL MOVE. Try again: ')
    s.board.print()

             
def main():
    tokens = [Game.X, Game.O]
    players = []
    for playeri in range(len(tokens)):
      printf("%s Player: Enter name, or press [ENTER] for AI: " % tokens[playeri])
      name = sys.stdin.readline()[:-1]
      if name:
        player = User(token=tokens[playeri], name=name)
      else:
        player = AI(token=tokens[playeri])
      players.append(player)     
    while True:
      board = Board(tokens)
      game = Game(tokens, players, board).play()
      printf("Play again? [Y/n]: ")
      again = sys.stdin.readline()[:-1]
      if again in "NnQq":
        break

  
main()
