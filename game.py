import numpy as np
import rl

class Game:

    def __init__(self):
        self.shape = (3,3,3,3,3,3,3,3,3,9,)
        rl.Q(reward, self.shape)
        self.state = np.zeros((3,3,), int)

    def start(self):
        player = a
        while not self.is_over():
            val, move = yield
            self.state[move] = val

    def is_over(self):
        # all spots taken up
        if 0 not in self.state:
            return True

        # winning column
        if np.any(
            np.logical_and(
                np.all(self.state == self.state[0,:], axis=0),
                np.all(self.state > 0, axis=0)
            )
        ):
            return True

        # winning row
        if np.any(
            np.logical_and(
                np.all(self.state == self.state[:,0], axis=1),
                np.all(self.state > 0, axis=1)
            )
        ):
            return True

        # winning diagonal
        if np.all(np.diag(self.state) > 0) and \
            np.all(self.state[0,0] == np.diag(self.state)):
            return True

        rot = np.rot90(self.state)
        if np.all(np.diag(rot) > 0) and \
            np.all(rot[0,0] == np.diag(rot)):
            return True

        return False

def reward(state):
    return 0
