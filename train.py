import game as g
import player as p
import random
import signal
import sys

game = g.Game()
player_1 = p.Player(1, game)
player_2 = p.Player(2, game)

try:
    player_1.q.load('player_1.npy')
except Exception:
    pass

try:
    player_2.q.load('player_2.npy')
except Exception:
    pass

def main():
    print('starting new game')
    game.anew()
    p = random.choice([player_1, player_2])
    while not game.is_over():
        p = player_1 if p is player_2 else player_2
        p.play()
        print(game.state)
        p.update()
    if game.result(1) == 'win':
        player_1.won()
        player_2.lost()
    if game.result(2) == 'win':
        player_1.lost()
        player_2.won()

def signal_handler(signal, frame):
    player_1.q.store('player_1')
    player_2.q.store('player_2')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

while True:
    main()
