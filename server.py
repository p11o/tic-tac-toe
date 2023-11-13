import tornado.ioloop
import tornado.web
import player as p
import game as g
import json
import numpy as np

CPU = 1
CLIENT = 2
game = g.Game()
player = p.Player(CPU, game)
try:
    player.q.load('player_1.npy')
except Exception as e:
    print('couldnt load stuff')
    print(e)

class ClientHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, PUT, GET, OPTIONS')

    def put(self):
        body = json.loads(self.request.body)
        coords = body['coords']
        if not game.is_over():
            game.state[tuple(coords)] = CLIENT

        self.write(json.dumps({
            'board': game.state.tolist(),
            'over': game.is_over()
        }))

    def options(self):
        pass

        
class RobotHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, PUT, GET, OPTIONS')

    def options(self):
        pass

    def put(self):
        print('game state:')
        print(game.state)
        print('game probs:')
        print(player.q.table[tuple(game.state.flatten())].reshape((3,3)))
        if not game.is_over():
            player.play()

        self.write(json.dumps({
            'board': game.state.tolist(),
            'over': game.is_over()
        }))


class GameHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, PUT, GET, OPTIONS')

    def options(self):
        pass

    def post(self):
        if game.is_over():
            player.play()
            player.update()
        try:
            player.q.load('player_1.npy')
        except Exception as e:
            print('couldnt load stuff')
            print(e)
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
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
    
