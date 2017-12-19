# Imports
import tornado.ioloop
import tornado.web
import tornado.template
from pymongo import MongoClient
from bson.json_util import dumps
from bson.json_util import loads

# Conexão MongoDB
client = MongoClient('localhost', 27017)
db = client.ootz_geo
ceps = db.ceps
cidades = db.cidades
estados = db.estados

class Home(tornado.web.RequestHandler):
    def get(self):
        self.render("views/index.html")

def make_app():
    return tornado.web.Application([
        (r"/", Home),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()