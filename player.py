import numpy as np
import random

class Player:
    def __init__(self, value, game, randomness=0.0):
        self.value = value
        self.game = game
        self.randomness = randomness
        # Assuming each of the 9 cells can be in 3 states (0, 1, 2), we have 3^9 possible states
        self.q_table = np.zeros((3**9, 9))  # 3**9 possible states, 9 possible actions
        self.reset()

    def reset(self):
        self.trajectory = []

    def play(self):
        state_index = self._state_to_index(self.game.state)
        if not self.game.is_over():
            move = self._choose_action(state_index)
            self.game.state[np.divmod(move, 3)] = self.value
        self.trajectory.append((state_index, move))

    def update(self, reward):
        while self.trajectory:
            state_action, next_state_action = self.trajectory.pop(), None
            if self.trajectory:
                next_state_action = self.trajectory[-1][0]
            self._update_q_table(state_action, next_state_action, reward)
    
    def _state_to_index(self, state):
        # Convert the 3x3 game state into a single integer for Q-table indexing
        flat_state = state.flatten()
        index = 0
        for power, value in enumerate(flat_state):
            index += (3 ** power) * value
        return index

    def _choose_action(self, state_index):
        possible_actions = [i for i, v in enumerate(self.game.state.flatten()) if v == 0]
        if random.random() < self.randomness:
            return random.choice(possible_actions)
        q_values = self.q_table[state_index, possible_actions]
        return possible_actions[np.argmax(q_values)]

    def _update_q_table(self, state_action, next_state_action, reward, alpha=0.5, gamma=0.9):
        state_index, action = state_action
        current_value = self.q_table[state_index, action]
        future_value = 0 if next_state_action is None else np.max(self.q_table[next_state_action])
        self.q_table[state_index, action] = (1 - alpha) * current_value + alpha * (reward + gamma * future_value)

    def save_model(self):
        np.save(f'player_{self.value}_model.npy', self.q_table)

    def load_model(self):
        self.q_table = np.load(f'player_{self.value}_model.npy')