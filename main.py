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

    def ResponseWithJson(self,return_code,est_json):
        self.write(json.dumps({"return_code": return_code, "data": est_json}, default=json_util.default))

class Home(DefaultHandler):
    def get(self):
        self.render("views/index.html")

class allEstados(DefaultHandler):
    def initialize(self):
        super(allEstados, self).initialize()

    def get(self):
        dados = estados.find({}, {'_id': False})
        estado_list = []
        if dados.count() == 0:
            with codecs.open('data/uf.csv') as ficheiro:
                reader = csv.reader(ficheiro)
                for linha in reader:
                    estado = {
                        "estado_id": linha[0],
                        "estado_uf": linha[1],
                        "estado": linha[2]
                    }
                    estado_list.append(estado)
            estados.insert_many(estado_list)
            self.ResponseWithJson(200,estado_list)
        else:
            for dado in dados:
                estado_list.append(dado)
            self.ResponseWithJson(200,estado_list)

class allCidades(DefaultHandler):
    def initialize(self):
        super(allCidades, self).initialize()

    def get(self,uf):
        if len(uf) == 2:
            ufUpper = uf.upper()
            dados = cidades.find({"estado_uf": ufUpper}, {"_id": False})
            cidade_list = []
            if dados.count() == 0:
                print("entrou")
                with codecs.open('data/cidades.csv') as ficheiro:
                    reader = csv.reader(ficheiro)
                    for linha in reader:
                        cidade = {
                            "cidade_ibge": linha[0],
                            "estado_uf": linha[1],
                            "cidade_nome": linha[2]
                        }
                        cidade_list.append(cidade)
                cidades.insert_many(cidade_list)
                cidade_list = []
                dadosCriados = cidades.find({"estado_uf": ufUpper}, {"_id": False})
                for dado in dadosCriados:
                    cidade_list.append(dado)
                self.ResponseWithJson(200,cidade_list)
            else:
                for dado in dados:
                    cidade_list.append(dado)
                self.ResponseWithJson(200,cidade_list)
                
        else:
            self.ResponseWithJson(404,"Digite uma sigla válida")

def make_app():
    return tornado.web.Application([
        (r"/", Home),
        (r"/estados", allEstados),
        (r"/cidades/(.*)", allCidades),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()