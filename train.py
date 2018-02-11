import game as g
import player as p
import random
import signal
import sys

game = g.Game()
player_1 = p.Player(1, game, randomness=0.5)
player_2 = p.Player(2, game, randomness=0.3)

try:
    player_1.q.load('player_1.npy')
except Exception:
    print('failed loading stuff')
    pass

try:
    player_2.q.load('player_2.npy')
except Exception:
    print('failed loading stuff')
    pass

def main():
    print('starting new game')
    game.anew()
    p = random.choice([player_1, player_2])
    while not game.is_over():
        p = player_1 if p is player_2 else player_2
        p.play()
        print(game.state)
        if not game.is_over():
            p.update()
    if game.result(1) == 'win':
        player_1.won()
        player_2.lost()
    elif game.result(2) == 'win':
        player_1.lost()
        player_2.won()
    else:
        player_1.tied()
        player_2.tied()

def signal_handler(signal, frame):
    player_1.q.store('player_1')
    player_2.q.store('player_2')
    print('stored stuff')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

while True:
    main()
