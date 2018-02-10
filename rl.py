import numpy as np

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

    def update(self, s0, s1, alpha=0.3, gamma=0.7):
        ds0 = self.discretize(s0)
        ds1 = self.discretize(s1)
        s1max = self.argmax(ds1)
        reward = self.r(s0)
        # (1 - a)(Q[s0,a0]) + a(R[s0,a0] + g * Qmax[s1,a1])
        value = ((1 - alpha) * self.table[ds0]) + (alpha * (reward + (gamma * self.table[s1max])))
        # print('ds0', ds0, s0, 'ds1', ds1, 'reward', reward, 'q[s0]', self.table[ds0], 'q[s1]', self.table[ds1], 'value', value)
        self.table[ds0] = value
        return self.table

    def argmax(self, state):
        *state, _ = state
        action_indexes = self.actions_filter(state)
        allowed_states = (*state, action_indexes)
        # print('allowed', allowed_states, 'action indexes', action_indexes)
        # print('table2', self.table[allowed_states])
        # print('allowed', allowed_states, self.table.shape)

        best_action = np.argmax(self.table[allowed_states])
        #print('chose', best_action, 'mapping with', action_indexes, state)
        ret = *state, action_indexes[best_action]
        #print('argmax', ret)
        return ret

    def learn(self, states, iterations=10, alpha=0.3, gamma=0.9, callback=None):
        for i in range(iterations):
            #print('starting iteration {}'.format(i))
            states_iter = states()
            try:
                s0 = next(states_iter)
            except StopIteration:
                continue
            for s1 in states_iter:
                #print(s0)
                self.update(s0, s1, alpha, gamma)
                s0 = s1
            # include last state
            self.table[self.discretize(s0)] += self.r(s0)
            if callback is not None:
                callback()
        # print('table', self.table)

    def store(self, filename):
        np.save(filename, self.table)

    def load(self, filename):
        self.table = np.load(filename)
