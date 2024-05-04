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
player = p.Player(CPU, game, randomness=0.1)  # Assume some randomness for player moves

def _load_model():
    try:
        player.load_model('player_model.npy')  # Assuming 'player_model.npy' is your model file
    except Exception as e:
        logging.info(f'Failed to load model: {str(e)}')

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
        if not game.is_over():
            player.play()
            player.update(0)  # Ensure the update method has the correct parameters if needed

        self.write(json.dumps({
            'board': game.state.tolist(),
            'over': game.is_over()
        }))

class GameHandler(CORSHandler):
    def post(self):
        if game.is_over():
            player.play()
            player.update(0)
        _load_model()
        game.reset()
        player.reset()
        self.write(json.dumps({
            'board': game.state.tolist(),
            'over': game.is_over()
        }))

    def get(self):
        self.write(json.dumps({
            'board': game.state.tolist(),
            'over': game.is_over()
        }))

def make_app():
    return tornado.web.Application([
        (r"/client/move", ClientHandler),
        (r"/robot/move", RobotHandler),
        (r"/game", GameHandler),
    ], autoreload=True)

if __name__ == "__main__":
    logging.getLogger("tornado.access").propagate = False
    app = make_app()
    app.listen(8001)
    tornado.ioloop.IOLoop.current().start()
