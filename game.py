import numpy as np

class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.state = np.zeros((3, 3), dtype=int)

    def result(self, player):
        return self._result(self.state, player)

    def is_over(self):
        # Explicitly handle the possibility of multiple elements in the result check
        return np.any([self.result(1) is not None, self.result(2) is not None])

    def _win(self, state, player):
        winning_conditions = [
            np.all(state == player, axis=0).any(),  # Check if any column is a win
            np.all(state == player, axis=1).any(),  # Check if any row is a win
            np.all(np.diag(state) == player),       # Check main diagonal
            np.all(np.diag(np.fliplr(state)) == player)  # Check secondary diagonal
        ]
        return any(winning_conditions)

    def _result(self, state, player):
        if self._win(state, player):
            return 'win'
        elif self._win(state, 3 - player):
            return 'lose'
        elif np.all(state != 0):
            return 'draw'
        return None
