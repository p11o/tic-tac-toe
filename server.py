import tornado.ioloop
import tornado.web
import player as p
import game as g
import json

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


CPU = 1
CLIENT = 2
game = g.Game()
player = p.Player(CPU, game)

def _load_model():
    try:
        player.load_model()
    except Exception as e:
        logging.info(f'Failed to load model {e}')


_load_model()


class CORSHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, PUT, GET, OPTIONS')


    def options(self):
        pass


class ClientHandler(CORSHandler):
    def put(self):
        body = json.loads(self.request.body)
        coords = body['coords']
        if not game.is_over():
            game.state[tuple(coords)] = CLIENT

        self.write(json.dumps({
            'board': game.state.tolist(),
            'over': game.is_over()
        }))


class RobotHandler(CORSHandler):
    def put(self):
        logging.info('game state:')
        logging.info(game.state)
        logging.info('game probs:')
        logging.info(player.table(game.state.flatten()))
        if not game.is_over():
            player.play()

        self.write(json.dumps({
            'board': game.state.tolist(),
            'over': game.is_over()
        }))


class GameHandler(CORSHandler):
    def post(self):
        if game.is_over():
            player.play()
            player.update()
        _load_model()
        game.reset()
        player.reset()
        logging.info(f"{game.state.tolist()}")
        logging.info(f"{game.is_over()}")
        self.write(json.dumps({
            'board': game.state.tolist(),
            'over': game.is_over()
        }))

    def get(self):
        logging.info(f"{game.state.tolist()}")
        logging.info(f"{game.is_over()}")
        self.write(json.dumps({
            'board': game.state.tolist(),
            'over': game.is_over()
        }))


def make_app():
    return tornado.web.Application([
        (r"/client/move", ClientHandler),
        (r"/robot/move", RobotHandler),
        (r"/game", GameHandler),
    ], autoreload=True  )

if __name__ == "__main__":
    logging.getLogger("tornado.access").propagate = False
    app = make_app()
    app.listen(8001)
    tornado.ioloop.IOLoop.current().start()
    
