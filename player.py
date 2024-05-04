
# player.py
import numpy as np
import random

class Player:
    def __init__(self, value, game, randomness=0.0):
        self.value = value
        self.game = game
        self.randomness = randomness
        self.q_table = np.zeros((3**9, 9)) + 1.0  # Initial optimism with small values

    def reset(self):
        self.trajectory = []

    def play(self):
        state_flat = tuple(self.game.state.flatten())
        if not self.game.is_over():
            move = self._choose_action(state_flat)
            self.game.state[np.divmod(move, 3)] = self.value
        self.trajectory.append((state_flat, move))

    def update(self, reward):
        while self.trajectory:
            state_action, next_state_action = self.trajectory.pop(), None
            if self.trajectory:
                next_state_action = self.trajectory[-1][0]
            self._update_q_table(state_action, next_state_action, reward)

    def _choose_action(self, state):
        possible_actions = [i for i, v in enumerate(state) if v == 0]
        if random.random() < self.randomness:
            return random.choice(possible_actions)
        q_values = [self.q_table[state][a] for a in possible_actions]
        return possible_actions[np.argmax(q_values)]

    def _update_q_table(self, state_action, next_state_action, reward, alpha=0.5, gamma=0.9):
        state, action = state_action
        current_value = self.q_table[state][action]
        future_value = 0 if next_state_action is None else np.max(self.q_table[next_state_action])
        self.q_table[state][action] = (1 - alpha) * current_value + alpha * (reward + gamma * future_value)
