import game as g
import player as p
import random
import signal
import sys
import logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO)



game = g.Game()
player_1 = p.Player(1, game, randomness=0.0)
player_2 = p.Player(2, game, randomness=0.0)


def _load(player, model):
    try:
        player.q.load(f'{model}.npy')
    except Exception:
        logging.info('Failed to load model')
        pass


_load(player_1, 'player_1')
_load(player_2, 'player_2')


def signal_handler(signal, frame):
    player_1.q.store('player_1')
    player_2.q.store('player_2')
    logging.info('Saved models')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def main():
    game.reset()
    player_1.reset()
    player_2.reset()
    p = random.choice([player_1, player_2])
    while not game.is_over():
        p.play()
        p = player_1 if p is player_2 else player_2
    player_1.play()
    player_2.play()
    player_1.update()
    player_2.update()


for i in range(1001):
    main()
    if i % 100 == 0 and i > 0:
        logging.info(f"Played {i} games...")

logging.info("Saving models")
player_1.q.store('player_1')
player_2.q.store('player_2')
