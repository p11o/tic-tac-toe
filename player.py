import rl
import torch
import torch.nn as nn
import torch.optim as optim
import functools

class Player:

    def __init__(self, value, env, randomness=0.0):
        self.value = value # 1 or 2 for first or second player
        self.shape = (9, 9)
        self.other = 2 if value == 1 else 1
        self.env = env
        self.trajectory = []
        self.q = rl.QNet(
            self.reward(),
            self.shape,
            mask=action_mask,
            randomness=randomness
        )

    def reset(self):
        self.trajectory = []

    def play(self):
        # print(f"play(): Player {self.value}")
        env = self.env
        move = -1 # set move to -1 if end of game
        state = env.state.flatten().clone()
        # print(f"play(): Player {self.value} {state=}")
        if not env.is_over():
            argmax = self.q.argmax(state)
            move = argmax[-1]
            env.state[to_coords(move)] = self.value
            # record trajectory (only needed for training)
            # print(f"play(): Player {self.value} {state} {move}")
            state_action = torch.cat([state, torch.tensor([move])])
            self.trajectory.append(state_action)
        elif env.result(self.value) == 'lose':
            self.trajectory.append(torch.cat([state, torch.tensor([move])]))
            

    def update(self):
        # print(f"update(): Player {self.value}")
        criterion = nn.MSELoss()
        optimizer = optim.SGD(self.q.table.parameters(), lr=0.005)

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

        for state, _ in pairs:
            state = state[:-1]
            target = torch.zeros(self.shape[1]) # output size
            mask = action_mask(state)
            for i in torch.nonzero(mask).flatten():
                i = i.item()
                modified_state = state.clone()
                modified_state[i] = self.value
                reward = self.q.reward(modified_state)
                target[i] = reward.item()
            

            optimizer.zero_grad()

            # Forward pass to get outputs from QModel
            prediction = self.q.table(state)

            # Calculate loss
            loss = criterion(prediction, target)
            
            # Backward pass and optimize
            loss.backward()
            optimizer.step()
        return loss.item()



    # reward is always zero except for last step
    def reward(self):
        def fn(state):
            reward = 0.0
            state = state.reshape((3,3,))
            if self.env.is_over(state):
                result = self.env.result(self.value)
                if result == 'win':
                    reward = 1.0
                elif result == 'draw':
                    reward = 0.5
                else:
                    reward = -1.0

            return reward
        return fn


    

# def actions_filter(state):
#     # map from cartesion (x, y) to 0-8
#     zeros = np.argwhere(np.array(state) == 0).flatten()
#     return zeros

def action_mask(state):
    return torch.where(torch.tensor(state) == 0, 1, 0)

def to_coords(move):
    x = move // 3
    y = move % 3
    return x,y,

