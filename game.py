import numpy as np

class Game:

    def __init__(self):
        self.reset()

    def reset(self):
        self.state = np.zeros((3,3,), int)

    def result(self, player):
        return result(self.state, player)

    def is_over(self, state=None):
        state = self.state if state is None else state

        return result(state, 2) is not None


def result(state, player):
    # winning column
    if (
        np.any(np.all(state == player, axis=0)) or
        np.any(np.all(state == player, axis=1)) or
        np.all(np.diag(state) == player) or
        np.all(np.diag(np.rot90(state)) == player)
    ):
        return 'win'
    
    other = 3 - player
    if (
        np.any(np.all(state == other, axis=0)) or
        np.any(np.all(state == other, axis=1)) or
        np.all(np.diag(state) == other) or
        np.all(np.diag(np.rot90(state)) == other)
    ):
        return 'lose'

    # all spots taken up
    if 0 not in state:
        return 'draw'
    
    return None
