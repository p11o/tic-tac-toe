import numpy as np
import random

def default_actions_filter(state):
    return [0]

def default_discretizer(state):
    return state

class Q:

    def __init__(self, r, shape, discretize=default_discretizer, randomness=0,
                 actions_filter=default_actions_filter, table=None):
        """
        Initializes the Q function.
        r is the reward function.
        """
        self.r = r
        self.discretize = discretize
        self.table = np.zeros(shape) if table is None else table
        self.table.fill(1.0)
        self.actions_filter = actions_filter
        self.randomness = randomness

    def update(self, s0, s1, alpha=0.5, gamma=0.8, terminal=False):
        ds0 = self.discretize(s0)
        ds1 = self.discretize(s1)

        # terminal state has no next state, so return reward
        if terminal:
            self.table[*ds0] = self.r(s0[:-1])
            return self.table

        # remove action
        s1max = self.argmax(ds1[:-1])
        reward = self.r(s1[:-1])

        value = ((1 - alpha) * self.table[*ds0]) + (alpha * (reward + (gamma * self.table[*s1max])))
        # print(f'updating {ds0} {self.table[*ds0]} to {value}, reward {reward} of {s1[:-1]}')
        self.table[*ds0] = value
        return self.table

    def argmax(self, state, deterministic=False):
        allowed_indices = self.actions_filter(state)
        allowed_q_table = self.table[*state][allowed_indices]
        if len(allowed_indices):
            if not deterministic and random.random() < self.randomness:
                best_action_idx = random.randint(0, len(allowed_q_table)) - 1
            else:
                best_action_idx = np.argmax(allowed_q_table)

            original_idx = allowed_indices[best_action_idx]
        else:
            original_idx = -1 # dummy index if no allowed moves

        return *state, original_idx

    def store(self, filename):
        np.save(filename, self.table)

    def load(self, filename):
        self.table = np.load(filename)
