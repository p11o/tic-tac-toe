import csv
import main
import os
import random
import sys

actions = {
    'buy': 0,
    'sell': 1,
    'hold': 2,
    'no': 3,
}

MAX_DAYS_OWNED = int(os.getenv('MAX_DAYS_OWNED', '10'))
MIN_DAYS_OWNED = int(os.getenv('MIN_DAYS_OWNED', '1'))
PERCENT_BUCKETS = int(os.getenv('PERCENT_BUCKETS', '10'))
PERCENT_RANGE = int(os.getenv('PERCENT_RANGE', '10'))


def percent_change_to_bucket(val):
    return min(PERCENT_BUCKETS - 1, max(0, int(
        val * PERCENT_BUCKETS / PERCENT_RANGE + int(PERCENT_BUCKETS / 2)
    )))


class Broker(main.Player):

    def __init__(self):
        # (days owned, % change since buy, % change past week, action)
        # (action: buy_1, (buy_10, buy_100), sell, hold, no)
        # for days owned field, 0 represents not owning
        shape = (MAX_DAYS_OWNED, PERCENT_RANGE, PERCENT_RANGE, 4,)
        print('shape', shape)
        super(Broker, self).__init__(shape)

    def get_action(self, state):
        """
        return an action for each stock
        Also stores the action made to the broker state
        action: {transaction: {buy/sell}, symbol, price, shares}
        """
        return super(Broker, self).get_action(state['broker'])

    def before_update(self, action, state):
        state['broker']['transaction'] = action
        return state['broker']

    def reward(self, state):
        """
        state is the state of the current stock that is owned
        """
        if self._owns_stock(state):
            return state['% change since buy']
        else:
            return -state['% change since sell'] / 2

    def _owns_stock(self, state):
        return state['days owned'] > 0

    def actions_filter(self, state):
        """
        state: see state: broker
        """
        if self._owns_stock(state):
            if state['days owned'] == MAX_DAYS_OWNED:
                return [actions['sell']]
            if state['days owned'] < MIN_DAYS_OWNED:
                return actions['hold']
            return [actions['sell'], actions['hold']]
        return [actions['buy'], actions['no']]

    def state_to_table(self, player_state):
        return [
            min(MAX_DAYS_OWNED - 1, player_state['days owned']),
            percent_change_to_bucket(player_state['% change since buy']),
            percent_change_to_bucket(player_state['% change past week']),
        ]


class StockMarket(main.Environment):

    def __init__(self, stock_history, symbol, cursor=None):
        # accept state as array of arrays
        # funds: number of stocks i can buy
        # return: my total return percentage...
        # state {
        #   'broker': {
        #     'days_owned' --- 0 represents not owning
        #     '% change since buy',
        #     '% change past week',
        #     'current price',
        #     'initial price',
        #     'return',
        #     'transaction',
        #   },
        #   'cursor': 0, -- the index of the stock history
        #   'symbol':
        #   'stock': [
        #     {
        #       open,
        #       close,
        #       volatility,
        #       price,
        #       p/e,
        #     }
        #   ],
        # }
        self._symbol = symbol
        self._cursor = cursor
        self._stock_history = stock_history
        state = self.reset()
        super(StockMarket, self).__init__(state)


    def reset(self):
        self.first = True
        self.state = {
            'cursor': self._cursor or 5,
            'stock': self._stock_history,
            'symbol': self._symbol,
            'broker': {
                'days owned': 0,
                '% change since buy': 0,
                '% change since sell': 0,
                '% change past week': 0,
                'initial price': 0, # could be since sell or buy
                'transaction': None,
                'return': 0,
            }
        }
        return self.state

    def is_over(self):
        """
        if there is no more stock data, then we done
        """
        return len(self.state['stock']) == self.state['cursor'] + 2

    def results(self):
        """
        returns a printable earnings
        """
        return self.state['broker']['return']

    def progress(self):
        """progress is run after all players commit. Iterate to next day of
        the market

        Update the state stocks field to have each of the current day's stock
        prices

        Update each players gains
        """
        curr = self.state['stock'][self.state['cursor']]
        self.state['cursor'] += 1
        next = self.state['stock'][self.state['cursor']]
        # approximate week delta
        BUSINESS_DAYS = 5
        last_week = self.state['stock'][self.state['cursor'] - BUSINESS_DAYS]

        broker = self.state['broker']
        transaction = broker['transaction']
        broker['% change past week'] = (next['open'] - last_week['open']) / last_week['open']
        if self.first:
            self.first = False
            broker['initial price'] = curr['open'] or 0.01
        if len(self.state['stock']) > self.state['cursor'] + 1:
            if transaction == actions['buy']:
                # print('buying', curr['open'])
                broker['days owned'] = 1

                # update for next iteration
                broker['initial price'] = curr['open']
                broker['% change since buy'] = 0
                broker['% change since sell'] = 0
            elif transaction == actions['sell']:
                broker['days owned'] = 0

                # update for next iteration
                broker['return'] += (curr['open'] - broker['initial price']) / broker['initial price']
                # print('selling', curr['open'], (curr['open'] - broker['initial price']) / broker['initial price'])
                # print('total return', broker['return'])
                broker['initial price'] = curr['open']
                broker['% change since buy'] = 0
                broker['% change since sell'] = 0
            elif transaction == actions['hold']:
                broker['days owned'] += 1

                # update for next iteration
                broker['% change since buy'] = (next['open'] - broker['initial price']) / broker['initial price']
                broker['% change since sell'] = 0
            elif transaction == actions['no']:
                broker['days owned'] = 0

                # update for next iteration
                broker['% change since buy'] = 0
                broker['% change since sell'] = (next['open'] - broker['initial price']) / broker['initial price']
        else:
            print('cursor', self.state['cursor'])
            raise Exception('need next data entry to continue')




stock_history = []
with open(sys.argv[1]) as f:
    reader = csv.DictReader(f)
    for row in reader:
        stock_history.append({
            'open': float(row['Open']),
            'close': float(row['Close']),
        })

players = [Broker()]
market = StockMarket(stock_history, 'tsla')

print('lengeth of history', len(stock_history))
# train
# players[0].randomness = 1
# end train
# run
players[0].randomness = 1
# end run
i = 1
buckets = {
    '<-3': 0,
    '-2': 0,
    '-1': 0,
    '-0': 0,
    '0': 0,
    '1': 0,
    '2': 0,
    '3': 0,
    '4': 0,
    '5': 0,
    '6': 0,
    '7': 0,
    '8': 0,
    '9': 0,
    '>10': 0,
}
STOCK_MODEL_PATH = 'stock-model.npy'
try:
    players[0].q.load(STOCK_MODEL_PATH)
except Exception as e:
    print(e)

while i < 1000:
    # print(f'randomness: {players[0].randomness}')
    market.reset()
    # train
    results = main.run(market, players)
    # players[0].randomness /= 1.005
    # end train
    # run
    # results = main.run(market, players, train=False)
    # end run

    bucket = None
    if 0 <= results <= 0.1:
        bucket = '0'
    elif -0.1 < results < 0:
        bucket = '-0'
    elif 0.1 < results <= 0.2:
        bucket = '1'
    elif -0.2 < results <= 0.1:
        bucket = '-1'
    elif 0.2 < results <= 0.3:
        bucket = '2'
    elif -0.3 < results <= -0.2:
        bucket = '-2'
    elif 0.3 < results <= 0.4:
        bucket = '3'
    elif results < -0.3:
        bucket = '<-3'
    elif results > 1:
        bucket = '>10'
    elif results > 0.9:
        bucket = '9'
    elif results > 0.8:
        bucket = '8'
    elif results > 0.7:
        bucket = '7'
    elif results > 0.6:
        bucket = '6'
    elif results > 0.5:
        bucket = '5'
    elif results > 0.4:
        bucket = '4'
    buckets[bucket] += 1
    stats = [ buckets[key] for key in buckets.keys() ]
    print(f'return: {results}, stats: {stats}' )
    i += 1

players[0].q.store(STOCK_MODEL_PATH)
