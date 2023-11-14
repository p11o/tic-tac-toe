import rl
import numpy as np
import functools

class Player:

    def __init__(self, value, env, randomness=0.0):
        self.value = value # 1 or 2 for first or second player
        shape = (3,3,3,3,3,3,3,3,3,9,)
        self.other = 2 if value == 1 else 1
        self.env = env
        self.trajectory = []
        self.q = rl.Q(
            self.reward(),
            shape,
            actions_filter=actions_filter,
            randomness=randomness
        )

    def reset(self):
        self.trajectory = []

    def play(self):
        env = self.env
        move = -1 # set move to -1 if end of game
        state = env.state.flatten().copy()
        if not env.is_over():
            argmax = self.q.argmax(state)
            move = argmax[-1]

            env.state[to_coords(move)] = self.value

        # record trajectory (only needed for training)
        state_action = [*state, move]
        self.trajectory = [*self.trajectory, state_action]

    def update(self):

        def _pair(acc, curr):
            pairs, prev = acc
            if prev is None:
                return ([], curr)
            pairs = [*pairs, (prev, curr)]
            return pairs, curr
        pairs, _ = functools.reduce(_pair, self.trajectory, ([], None))
        
        self.q.update(self.trajectory[-1], None, terminal=True)
        for s0, s1 in list(reversed(pairs)):
            self.q.update(s0, s1)


    # reward is always zero except for last step
    def reward(self):
        def fn(state):
            reward = 0.0
            state = np.array(state).reshape((3,3,))
            if self.env.is_over(state):
                result = self.env.result(self.value)
                if result == 'win':
                    # print(f'player {self.value} has won')
                    reward = 1.0
                elif result == 'draw':
                    # print(f'player {self.value} has drawn')
                    reward = 0.5
                else:
                    # print(f'player {self.value} has lost')
                    reward = -20.0

            return reward
        return fn


    

def actions_filter(state):
    # map from cartesion (x, y) to 0-8
    zeros = np.argwhere(np.array(state) == 0).flatten()

    return zeros

def to_coords(move):
    x = move // 3
    y = move % 3
    return x,y,

