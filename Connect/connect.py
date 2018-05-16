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

  def add(s, token):
    for row in range(s.height):
      if s[row] == s.SPACE:
        s[row] = token
        return True
    return False

  def __iter__(s):
    return iter(s.content)

  # returns None if out of range
  def __getitem__(s, i):
   return s.content[i]

  def __setitem__(s, i, value):
   s.content[i] = value
   
class Board:
  WIN_SIZE = 4
  WIDTH = 7
  HEIGHT = 6
  SPACE = ' '
  
  def __init__(s, tokens):
    s.cols = [Column(s.HEIGHT) for i in range(s.WIDTH)]
    s.tokens = tokens

  def full(s):
    return all([col.full() for col in s.cols])

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
          d = all([(coli + offset < s.WIDTH) and (rowi + offset < s.HEIGHT)
                   and (token == s.cols[coli + offset][rowi + offset]) for offset in offsets])           
          winner = h or v or d
          if winner:
            return token
    return winner

  def winning_move(s):
    def count(array):
      return sum([1 if x else 0 for x in array])

    def indexof(array, value):
      for i in range(len(array)):
        if array[i] == value:
           return i
      return None
                     
    for coli in range(s.WIDTH):
      for rowi in range(s.HEIGHT):
        token = s.cols[coli][rowi]
        offsets = range(s.WIN_SIZE)
        # Scans everything twice, but OK
        for token in s.tokens:
          # horizontal
          line = ([(coli + offset < s.WIDTH) and (token == s.cols[coli+offset][rowi])
                   for offset in offsets])
          if count(line) == (s.WIN_SIZE-1):
            offset = indexof(line, False)
            # Make sure the spot we want to play is on the board, not "3 in row up to the edge",
            # and that the spot is not above an empty space (gravity falls)
            #print("Testing horizontal move at (%s,%s,+(%s,0))" %(coli,rowi,offset))
            if (coli+offset < s.WIDTH and s.SPACE == s.cols[coli+offset][rowi]
                and (rowi==0 or not s.SPACE == s.cols[coli+offset][rowi-1])):
              #print("Playing horizontal move at (%s,%s,+(%s,0))" %(coli,rowi,offset))
              return coli+offset
                   
          # vertical
          line = ([(rowi + offset < s.HEIGHT) and (token == s.cols[coli][rowi + offset])
                   for offset in offsets])
          if count(line) == (s.WIN_SIZE-1):
            offset = indexof(line, False)
            #print("Testing vertical move at (%s,%s,+(0,%s))" %(coli,rowi,offset))
            if (rowi+offset < s.HEIGHT and s.SPACE == s.cols[coli][rowi+offset]
                and (rowi==0 or not s.SPACE == s.cols[coli][rowi-1])):
              #print("Playing vertical move at (%s,%s,+(0,%s))" %(coli,rowi,offset))
              return coli

          # diagonal up-right
          line = ([(coli + offset < s.WIDTH) and (rowi + offset < s.HEIGHT)
                   and (token == s.cols[coli + offset][rowi + offset]) for offset in offsets])           
          if count(line) == (s.WIN_SIZE-1):
            offset = indexof(line, False)
            #print("Testing diagonal move at (%s,%s,+(%s,%s)" %(coli,rowi,offset,offset))
            if (coli+offset < s.WIDTH and rowi+offset < s.HEIGHT
                and s.SPACE == s.cols[coli+offset][rowi+offset]
                and (rowi==0 or not s.SPACE == s.cols[coli+offset][rowi+offset-1])):
              #print("Playing diagonal move at (%s,%s,+(%s,%s)" %(coli,rowi,offset,offset))
              return coli+offset

          # diagonal up-left
          line = ([(coli - offset >= 0) and (rowi + offset < s.HEIGHT)
                   and (token == s.cols[coli - offset][rowi-offset]) for offset in offsets])           
          if count(line) == (s.WIN_SIZE-1):
            offset = indexof(line, False)
            #print("Testing diagonal move at (%s,%s,+(-s,%s)" %(coli,rowi,,offset,offset))
            if (coli-offset >= 0 and  rowi+offset < s.HEIGHT
                and s.SPACE == s.cols[coli-offset][rowi+offset]
                and (rowi==0 or not s.SPACE == s.cols[coli-offset][rowi+offset-1])):
              #print("Playing diagonal move at (%s,%s,+(-%s,%s)" %(coli,rowi,offset,offset))
              return coli-offset
    return None
                     
  def print(s):
    printf('\n')
    for rowi in range(s.HEIGHT-1, -1, -1):
      printf('|')
      for coli in range(s.WIDTH):
        printf(s.cols[coli][rowi])
      printf('|\n')
    printf('+%s+\n' % ('-' * s.WIDTH))
    printf(' %s \n' % ''.join([str(i) for i in range(s.WIDTH)]))

class AI:
  def __init__(s, token):
    s.name = "Marvin"
    s.token = token
    # Caller must install board soon!

  def move(s):
    # Win or avoid immediate loss if possible
    winning_move = s.board.winning_move()
    
    if winning_move is not None:
      # print("Playing win/blocking move")
      return winning_move
                     
    # random move
    start_coli = int(random.random() * s.board.WIDTH)
    for i in range(s.board.WIDTH):
      move_i = (start_coli + i) % s.board.WIDTH
      col = s.board.cols[move_i]
      if not col.full():
        return move_i
    raise Exception("Can't move!")

class User:
  def __init__(s, name, token):
    s.name = name
    s.token = token
    # Caller must install board soon!
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
      move = player.move() 
      try:
        if s.board.cols[move].add(player.token):
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
      for player in players:
        player.board = board
      Game(tokens, players, board).play()
      printf("Play again? [Y/n]: ")
      again = sys.stdin.readline()[:-1]
      if again in "NnQq":
        break



main()
