
# main.py
from game import Game
from player import Player
import random

def main():
    game = Game()
    player_1 = Player(1, game)
    player_2 = Player(2, game)

    for _ in range(1000):
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
        reward_p1 = 1 if result_p1 == 'win' else 0.5 if result_p1 == 'draw' else -1
        result_p2 = game.result(player_2.value)
        reward_p2 = 1 if result_p2 == 'win' else 0.5 if result_p2 == 'draw' else -1

        player_1.update(reward_p1)
        player_2.update(reward_p2)

if __name__ == "__main__":
    main()
