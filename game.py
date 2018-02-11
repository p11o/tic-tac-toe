import numpy as np

class Game:

    def __init__(self):
        self.anew()

    def anew(self):
        self.state = np.zeros((3,3,), int)
        print('set state', self.state)

    def result(self, player):
        return result(self.state, player)

    def is_over(self):
        return self.result(1) == 'win' or \
            self.result(2) == 'win' or \
            self.result(2) == 'draw'

def result(state, player):
    # winning column
    if np.any(np.all(state == player, axis=0)):
        return 'win'

    # winning row
    if np.any(np.all(state == player, axis=1)):
        return 'win'

    # winning diagonal
    if np.all(np.diag(state) == player):
        return 'win'

    rot = np.rot90(state)
    if np.all(np.diag(rot) == player):
        return 'win'

    # all spots taken up
    if 0 not in state:
        return 'draw'

    return None
