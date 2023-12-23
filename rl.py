import torch
import torch.nn as nn
import torch.optim as optim



# Define the neural network model
class QModel(nn.Module):
    """Takes state input, provides next action with max reward?"""
    def __init__(self, input_dim, output_dim):
        super(QModel, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, output_dim)

    def forward(self, x):
        x = torch.relu(self.fc1(x.float()))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        x = self.fc4(x)
        x = torch.tanh(x)
        return x



class RewardPredictionModel(nn.Module):
    """Returns reward value for given state"""
    def __init__(self, input_dim):
        super(RewardPredictionModel, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, 1)

    def forward(self, x):
        x = torch.relu(self.fc1(x.float()))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        x = self.fc4(x)
        x = torch.tanh(x)
        return x


def default_actions_filter(state):
    return [0]

def default_discretizer(state):
    return state


class QNet:

    def __init__(self, r, shape, discretize=default_discretizer, randomness=0,
                 mask=None, table=None):
        """
        Initializes the Q function.
        r is the reward function.
        """
        self.r = r
        self.mask = mask
        self.discretize = discretize
        self.table = QModel(*shape)
        self.reward = RewardPredictionModel(shape[0])
        self.randomness = randomness
        self.optimizer = optim.SGD(self.reward.parameters(), lr=0.005)
        self.reward_loss_function = nn.MSELoss()

    def update(self, s0, s1, alpha=0.5, gamma=0.8, terminal=False):
        ds0 = torch.tensor(self.discretize(s0[:-1]))
        if not terminal:
            ds1 = torch.tensor(self.discretize(s1[:-1]))

        # terminal state has no next state, so return reward
        if terminal:
            reward = self.r(ds0)

        else:
            s1max = self.argmax(ds1)
            r = self.r(ds1)

            s0_reward = self.reward(ds0)
            s1_reward = self.reward(s1max[:-1])

            reward = ((1 - alpha) * s0_reward) + (alpha * (r + (gamma * s1_reward)))
        
        # Forward pass
        reward = torch.tensor([reward])
        self.optimizer.zero_grad()
        # print(f"update() {ds0=}")
        outputs = self.reward(ds0)

        # Compute loss
        # print(f"update() {outputs=} {reward=}")
        loss = self.reward_loss_function(outputs, reward)

        # Backward pass and optimize
        loss.backward()
        self.optimizer.step()
        return loss.item()


    def argmax(self, state: torch.tensor):
        rewards = self.table(state)
        mask = self.mask(state)
        action = torch.argmax(self.mask(state) * rewards)
        if mask[action] != 1:
            if torch.all(mask == 0):
                action = -1
            else:
                nonzero_indices = torch.nonzero(mask).flatten()
                random_index = torch.randint(0, len(nonzero_indices), size=(1,)).item()
                action = nonzero_indices[random_index]

        argmax = torch.tensor((*state, action))
        # print(f"argmax: {state=} mask={self.mask(state)} {rewards=} {argmax=}")
        
        return argmax

    def store(self, filename):
        torch.save(self.table.state_dict(), f"{filename}_q.pth")
        torch.save(self.reward.state_dict(), f"{filename}_reward.pth")

    def load(self, filename):
        self.table.load_state_dict(torch.load(f"{filename}_q.pth"))
        self.reward.load_state_dict(torch.load(f"{filename}_reward.pth"))




# class Q:

#     def __init__(self, r, shape, discretize=default_discretizer, randomness=0,
#                  actions_filter=default_actions_filter, table=None):
#         """
#         Initializes the Q function.
#         r is the reward function.
#         """
#         self.r = r
#         self.discretize = discretize
#         self.table = np.zeros(shape) if table is None else table
#         self.table.fill(1.0)
#         self.actions_filter = actions_filter
#         self.randomness = randomness

#     def update(self, s0, s1, alpha=0.5, gamma=0.8, terminal=False):
#         ds0 = self.discretize(s0)
#         ds1 = self.discretize(s1)

#         # terminal state has no next state, so return reward
#         if terminal:
#             self.table[*ds0] = self.r(s0[:-1])
#             return self.table

#         s1max = self.argmax(ds1[:-1])
#         reward = self.r(s1[:-1])

#         value = ((1 - alpha) * self.table[*ds0]) + (alpha * (reward + (gamma * self.table[*s1max])))
#         # print(f'updating {ds0} {self.table[*ds0]} to {value}, reward {reward} of {s1[:-1]}')
#         self.table[*ds0] = value
#         return self.table

#     def argmax(self, state, deterministic=False):
#         allowed_indices = self.actions_filter(state)
#         allowed_q_table = self.table[*state][allowed_indices]
#         if len(allowed_indices):
#             if not deterministic and random.random() < self.randomness:
#                 best_action_idx = random.randint(0, len(allowed_q_table)) - 1
#             else:
#                 best_action_idx = np.argmax(allowed_q_table)

#             original_idx = allowed_indices[best_action_idx]
#         else:
#             original_idx = -1 # dummy index if no allowed moves

#         return *state, original_idx

#     def store(self, filename):
#         np.save(filename, self.table)

#     def load(self, filename):
#         self.table = np.load(filename)
