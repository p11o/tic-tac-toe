import numpy as np
import random

def default_actions_filter(state):
    return [0]

def default_discretizer(state):
    return state

class Q:

    def __init__(self, r, shape, discretize=default_discretizer,
                 actions_filter=default_actions_filter, table=None):
        """
        Initializes the Q function.
        r is the reward function.
        """
        self.r = r
        self.discretize = discretize
        self.table = np.zeros(shape) if table is None else table
        self.actions_filter = actions_filter

    def update(self, s0, s1, alpha=0.1, gamma=0.9):
        ds0 = self.discretize(s0)
        ds1 = self.discretize(s1)
        action_indexes = self.actions_filter(s1)
        s1max = self.argmax(ds1, action_indexes, randomness=0)
        reward = self.r(s0)
        value = ((1 - alpha) * self.table[ds0]) + (alpha * (reward + (gamma * self.table[s1max])))
        self.table[ds0] = value
        return s1max

    def argmax(self, state, action_indexes, randomness=None):
        *state, _ = state
        allowed_states = (*state, action_indexes)
        # check if randomness is set or if any values haven't been populated
        if random.random() < randomness:
            best_action = np.random.choice(range(len(self.table[allowed_states])))
        else:
            best_action = np.argmax(self.table[allowed_states])
        ret = *state, action_indexes[best_action]
        return ret

    def store(self, filename):
        np.save(filename, self.table)

    def load(self, filename):
        self.table = np.load(filename)
