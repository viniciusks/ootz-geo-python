# -*- coding: utf-8 -*-
# Imports
import csv
import json
import codecs
import tornado.ioloop
import tornado.web
import tornado.template
from pymongo import MongoClient
from bson.json_util import dumps
from bson.json_util import loads
from bson import json_util

# Conexão MongoDB
client = MongoClient('localhost', 27017)
db = client.ootz_geo
ceps = db.ceps
cidades = db.cidades
estados = db.estados

class DefaultHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.set_header("Content-Type", "application/json") 
        self.content_type = 'application/json'

    def ResponseWithJson(self,return_code=0,json=0):
        #self.write(json.dumps({"return_code": return_code, "data": json}, default=json_util.default))
        print("FAAAALA GALERA!!!")
        print(return_code)
        print(json)

class Home(DefaultHandler):
    def get(self):
        self.render("views/index.html")

class allEstados(DefaultHandler):
    def get(self):
        dados = estados.find()
        print(dados.count())
        estado_list = []
        if dados.count() == 0:
            with codecs.open('data/uf.csv') as ficheiro:
                reader = csv.reader(ficheiro)
                for linha in reader:
                    estado = {
                        "estadoID": linha[0],
                        "estadoUf": linha[1],
                        "estadoNome": linha[2]
                    }
                    estado_list.append(estado)
            estados.insert_many(estado_list)
            self.write(json.dumps({"return_code": 200, "data": estado_list}, default=json_util.default))
        else:
            for dado in dados:
                estado_list.append(dado)
            self.write(json.dumps({"return_code": 200, "data": estado_list}, default=json_util.default))            

def make_app():
    return tornado.web.Application([
        (r"/", Home),
        (r"/estados", allEstados),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()