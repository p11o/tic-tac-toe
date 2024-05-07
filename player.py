import numpy as np
import random



class BaseQAgent:
    def __init__(self, num_states, num_actions, randomness=0.1, alpha=0.5, gamma=0.9):
        self.num_states = num_states
        self.num_actions = num_actions
        self.randomness = randomness
        self.alpha = alpha
        self.gamma = gamma
        self.q_table = np.zeros((num_states, num_actions))
        self.trajectory = []
    
    def reset(self):
        self.trajectory = []

    def choose_action(self, state_index):
        if random.random() < self.randomness:
            return random.choice(range(self.num_actions))
        return np.argmax(self.q_table[state_index])

    def update(self, reward):
        while self.trajectory:
            state, action, next_state = self.trajectory.pop()
            current_q_value = self.q_table[state, action]
            future_q_value = np.max(self.q_table[next_state]) if next_state is not None else 0
            self.q_table[state, action] = (1 - self.alpha) * current_q_value + self.alpha * (reward + self.gamma * future_q_value)
            reward = self.q_table[state, action]

    def save_model(self, filename):
        np.save(filename, self.q_table)

    def load_model(self, filename):
        try:
            self.q_table = np.load(filename)
        except Exception:
            print(f"Unable to load model {filename}")


class Player(BaseQAgent):
    def __init__(self, value, game, randomness=0.1):
        num_states = 3**9  # For a 3x3 Tic-Tac-Toe board
        num_actions = 9  # Each cell is a possible action
        super().__init__(num_states, num_actions, randomness)
        self.game = game
        self.value = value

    def play(self):
        state_index = self._state_to_index(self.game.state)
        q_values = None
        if not self.game.is_over():
            action, q_values = self.choose_action(state_index)
            self.game.state[np.divmod(action, 3)] = self.value
            new_state_index = self._state_to_index(self.game.state)
        else:
            new_state_index = state_index
            action = None

        if action is not None:
            self.trajectory.append((state_index, action, new_state_index))
        
        return q_values


    def choose_action(self, state_index):
        # Identify the empty cells
        empty_cells = [i for i, v in enumerate(self.game.state.flatten()) if v == 0]
        if not empty_cells:
            return None, None  # No action possible

        # Filter Q-values to only include empty cells
        q_values = self.q_table[state_index, empty_cells]
        if random.random() < self.randomness:
            q_values = np.copy(q_values)
            q_values[:] = -1.0
            return random.choice(empty_cells), (empty_cells, q_values)

        return empty_cells[np.argmax(q_values)], (empty_cells, q_values)


    def _state_to_index(self, state):
        flat_state = state.flatten()
        index = 0
        for power, value in enumerate(flat_state):
            index += (3 ** power) * value
        return index

    def save_model(self, filename=None):
        super().save_model(filename or f"player_{self.value}_model.npy")

    def load_model(self, filename=None):
        super().load_model(filename or f"player_{self.value}_model.npy")