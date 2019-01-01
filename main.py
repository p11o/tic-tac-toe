import uuid
import copy
import rl
import numpy as np
# environment is set
# a player (of many) takes action
#   (action is internal which needs to be translated to external environment)
# environment responds
# player calculates reward, updates table
# loop to step 2

class Player:

    def __init__(self, shape):
        self.id = uuid.uuid4()
        self.prev = None
        self.curr = None
        self.randomness = None
        self.q = rl.Q(
            lambda state: self.reward(state),
            shape,
            actions_filter=self.actions_filter
        )

    def get_action(self, state, randomness=0):
        """
        state: (player state, stock data)
        """
        table = self.state_to_table(state)
        q_state = np.append(table, [0]) # [0] is a dummy value
        optimal = self.q.argmax(
            q_state,
            self.actions_filter(state),
            self.randomness
        )
        # last element in the array is the action
        return optimal[-1]


    def update(self, action, state):
        """Update the q table for the player"""
        if self.prev:
            self.q.update(self.prev, self.curr)
        self.prev = self.curr

    def reward(self, state):
        """returns reward based on state. Used by the Q table.  It is best
        to implement a incremental reward based on the state."""
        raise Exception('Not implemented')

    def actions_filter(self, state):
        """Return possible actions based on the state."""
        raise Exception('Not implemented')

    def state_to_table(self, state):
        """converts environment state to features in q table"""
        raise Exception('Not implemented')

    def before_update(self, action, state):
        """Hook to optionally implement.  Runs before player update.  It should
        store a small historical that the player can compute the discrete state
        from."""
        raise Exception('Not implemented')


class Environment:

    def __init__(self, state):
        self.state = state

    def reset():
        raise Exception('Not implemented')

    def accept(self, player, train):
        """request action from player, update state of the environment, and
        update the q table of the other players"""
        action = player.get_action(self.state)

        self.curr = copy.deepcopy(player.before_update(action, self.state))
        if train:
            player.update(action, self.state)

    def update(self, action, player):
        """This action is overridden per game environment.  It knows how to
        accept an action and update the environment state."""
        pass

    def is_over(self):
        """Check if game is over"""
        pass

    def results(self):
        """return some printable thing to represent the game"""
        pass

    def progress(self):
        """implement if there are updates to the state besides what is done
        by players"""
        pass


def run(env, players, train=True):
    while not env.is_over():
        for player in players:
            env.accept(player, train)
        env.progress()

    return env.results()
