import rl
import numpy as np
import game

class Player:

    def __init__(self, value, env):
        self.value = value # 1 or 2 for first or second player
        shape = (3,3,3,3,3,3,3,3,3,9,)
        self.prev = None
        self.curr = None
        self.env = env
        self.q = rl.Q(
            reward,
            shape,
            actions_filter=actions_filter,
            randomness=0.3
        )

    def play(self, env=None):
        env = self.env
        full_state = np.append(env.state.flatten(), [0]) # [0] is a dummy value
        self.curr = argmax = self.q.argmax(full_state, )
        move = argmax[-1]
        env.state[to_coords(move)] = self.value

    def update(self):
        if self.prev is not None:
            self.q.update(self.prev, self.curr, self.value)
        self.prev = self.curr

    def lost(self):
        # set the reward for
        print('setting table lost for player {}'.format(self.value))
        self.q.table[self.curr] = -1
        self.update()
        print(self.q.table[self.curr[:-1]])

    def won(self):
        print('setting table win for player {}'.format(self.value))
        self.q.table[self.curr] = 1
        self.update()
        print(self.q.table[self.curr[:-1]])

    def tied(self):
        #self.q.table[self.curr] = 0
        #self.update()
        pass

# reward is always zero except for last step
def reward(state):
    return 0

def actions_filter(state):
    # map from cartesion (x, y) to 0-8
    zeros = np.argwhere(np.array(state) == 0).flatten()

    return zeros

def to_coords(move):
    x = int(move / 3)
    y = move % 3
    return x,y

def state_to_board(state, p):
    coords = to_coords(state[-1])
    board = state[0:9].reshape((3,3,))
    board[coords] = p
    return board
    
