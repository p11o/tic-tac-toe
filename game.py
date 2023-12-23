import torch

class Game:

    def __init__(self):
        self.reset()

    def reset(self):
        self.state = torch.zeros((3,3,), dtype=torch.int32)

    def result(self, player):
        return _result(self.state, player)

    def is_over(self, state=None):
        state = self.state if state is None else state

        return _result(state, 2) is not None


def _win(state, player):
    # print(f"_win(): {state=} {player=}")
    return (
        torch.any(torch.all(state == player, axis=0)) or
        torch.any(torch.all(state == player, axis=1)) or
        torch.all(torch.diag(state) == player) or
        torch.all(torch.diag(torch.rot90(state)) == player)
    )


def _result(state, player):
    other_player = 3 - player
    if _win(state, player):
        return 'win'
    
    elif _win(state, other_player):
        return 'lose'

    # all spots taken up
    elif 0 not in state:
        return 'draw'
    
    return None
