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
        player.q.load(model)
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


PLAYERS = [player_1, player_2]

def main():
    players = random.sample(PLAYERS, k=2)
    game.reset()
    for p in players:
        p.reset()

    while not game.is_over():
        for p in players:
            p.play()

    loss = []
    for p in players:
        p.play()
        loss.append(p.update())
    return loss

print("HIIII")

for i in range(6_001):
    loss = main()
    if i % 100 == 0 and i > 0:
        print(f"{i} {loss=}", flush=True)
        logging.info("Saving models")
        player_1.q.store('player_1')
        player_2.q.store('player_2')
        logging.info(f"{player_1.env.state}")

