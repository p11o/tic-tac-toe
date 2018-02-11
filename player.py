import rl
import numpy as np
import game

class Player:

    def __init__(self, value, env, randomness=0):
        self.value = value # 1 or 2 for first or second player
        shape = (3,3,3,3,3,3,3,3,3,9,)
        self.prev = None
        self.curr = None
        self.env = env
        self.q = rl.Q(
            reward_wrap(value),
            shape,
            actions_filter=actions_filter,
            randomness=randomness
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
        self.q.table[self.curr] = -0.1
        self.update()

# reward is always zero except for last step
def reward_wrap(value):
    def reward(state):
        board = np.array(state[:-1]).reshape((3,3,))
        move = to_coords(state[-1])
        return 0.1 * count_in_path(board, move, value) 
    return reward

def count_in_path(board, coords, value):
    print('coords', coords)
    row, col = coords
    matching = len(np.where(board[:,col] == value))
    matching += len(np.where(board[row,:] == value))
    if row + col in [0, 2, 4]:
        matching += len(np.where(np.diag(board) == value))
        matching += len(np.where(np.diag(np.rot90(board)) == value))
    return matching

    

def actions_filter(state):
    # map from cartesion (x, y) to 0-8
    zeros = np.argwhere(np.array(state) == 0).flatten()

    return zeros

def to_coords(move):
    x = int(move / 3)
    y = move % 3
    return x,y,

def state_to_board(state, p):
    coords = to_coords(state[-1])
    board = state[0:9].reshape((3,3,))
    board[coords] = p
    return board
    
