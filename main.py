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
            discretize=self.state_to_table,
            actions_filter=self.actions_filter,
        )

    def get_action(self, state, thresholds=None):
        """
        state: (player state, stock data)
        """
        table = self.state_to_table(state)
        filtered_actions = self.actions_filter(state)

        *table_base, _ = table
        if thresholds:
            # print(filtered_actions)
            # for filtered_action in filtered_actions:
            #     print(self.q.table[(*table_base, filtered_action)])
            filtered_actions = [
                filtered_action
                for filtered_action in filtered_actions
                if (not thresholds.get(str(filtered_action))) or \
                    thresholds.get(str(filtered_action)) < self.q.table[(*table_base, filtered_action)]
            ]
            # print(filtered_actions)

        optimal = self.q.argmax(
            table,
            filtered_actions,
            self.randomness
        )
        # last element in the array is the action
        allowed = (*table_base, filtered_actions)
        return optimal[-1], self.q.table[optimal], self.q.table[allowed]


    def update(self, action, state):
        """Update the q table for the player"""
        if self.prev:
            self.q.update(
                self.prev,
                self.curr,
            )
        self.prev = copy.deepcopy(self.curr)

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
        from.  should"""
        raise Exception('Not implemented')


class Environment:

    def __init__(self, state):
        self.state = state

    def reset():
        raise Exception('Not implemented')

    def accept(self, player, train, thresholds=None):
        """request action from player, update state of the environment, and
        update the q table of the other players

        thresholds is a (action, score differential) pairing
        """
        action, *score = player.get_action(self.state, thresholds)

        copy.deepcopy(player.before_update(action, self.state))
        if train:
            player.update(action, self.state)
        return score

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

    def progress(self, score):
        """implement if there are updates to the state besides what is done
        by players"""
        pass


def run(env, players, train=True, thresholds=None):
    while not env.is_over():
        score = None
        for player in players:
            score = env.accept(player, train, thresholds)
        env.progress(score)

    return env.results()
