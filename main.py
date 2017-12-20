# Imports
import csv
import json
import codecs
import tornado.ioloop
import tornado.web
import tornado.template
import urllib3
import pycep_correios
from pycep_correios.excecoes import CEPInvalido
from pymongo import MongoClient
from bson.json_util import dumps
from bson.json_util import loads
from bson import json_util
import config

# Desabilitando warnings
urllib3.disable_warnings()

# Conexão MongoDB APP_CONFIG['mongodb']['host']
client = MongoClient(APP_CONFIG['mongodb']['host'], APP_CONFIG['mongodb']['port'])
# Database
db = client.ootz_geo
# Collections
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
        self.ResponseWithJson(1,"Ok")

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
            self.ResponseWithJson(1,estado_list)
        else:
            for dado in dados:
                estado_list.append(dado)
            self.ResponseWithJson(1,estado_list)

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
                self.ResponseWithJson(1,cidade_list)
            else:
                for dado in dados:
                    cidade_list.append(dado)
                self.ResponseWithJson(1,cidade_list)
                
        else:
            self.ResponseWithJson(0,"Digite uma sigla válida")

class ConsultaCep(DefaultHandler):
    def initialize(self):
        super(ConsultaCep, self).initialize()

    def get(self,cep_param):
        try:
            endereco = pycep_correios.consultar_cep(cep_param)
            cep = ceps.find_one({"cep": endereco["cep"]}, {"_id": False})
            if cep is None:
                ceps.insert_one(endereco)
                self.ResponseWithJson(1,endereco)
            else:
                self.ResponseWithJson(1,cep)
        except CEPInvalido:
            self.ResponseWithJson(0,"CEP inválido!")

def make_app():
    return tornado.web.Application([
        (r"/", Home),
        (r"/estados", allEstados),
        (r"/cidades/(.*)", allCidades),
        (r"/consulta/cep/(.*)", ConsultaCep),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8086)
    tornado.ioloop.IOLoop.current().start()