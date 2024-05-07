
# main.py
from game import Game
from player import Player
import random
import sys
import logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

WIN = 1
DRAW = 1
LOSS = -1
NONE = 0
RANDOMNESS = 0.9
EPISODES = 30_000

def reward(result):
    if result is None:
        return NONE
    elif result == 'win':
        return WIN
    elif result == 'draw':
        return DRAW
    else:
        return LOSS


def main():
    game = Game()
    player_1 = Player(1, game, RANDOMNESS)
    player_2 = Player(2, game, RANDOMNESS - 0.1)
    player_1.load_model()
    player_2.load_model()

    for episode in range(EPISODES):
        game.reset()
        players = [player_1, player_2]
        random.shuffle(players)

        while not game.is_over():
            for player in players:
                player.play()
                if game.is_over():
                    break

        # Determine rewards and update Q-tables
        result_p1 = game.result(player_1.value)
        result_p2 = game.result(player_2.value)

        player_1.update(reward(result_p1))
        player_2.update(reward(result_p2))
        if (episode + 1) % 1000 == 0:
            logging.info(f"Completed {episode + 1} iterations, randomness: {player_1.randomness}")
            # Save models after training
            player_1.save_model()
            player_2.save_model()
            player_1.randomness /= 1.1
            player_2.randomness /= 1.1

if __name__ == "__main__":
    main()
