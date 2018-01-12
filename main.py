# -*- coding: UTF-8 -*-
# Imports
import csv
import json
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

# Conexão MongoDB
client = MongoClient(config.APP_SETTINGS['mongodb']['host'], config.APP_SETTINGS['mongodb']['port'])

## -- CONEXÃO COM O MONGO DENTRO DO KUBERNETES -- ##
# uri = "mongodb://mongo-0.mongo:27017,mongo-1.mongo:27017,mongo-2.mongo:27017"
# client = MongoClient(uri)
## ---------------------------------------------- ##

# Database
db = client[config.APP_SETTINGS['database']]
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
    def get(self):
        # Procura as informações no database na collection estados
        dados = estados.find({}, {'_id': False})
        estado_list = []
        # Se dados.count() == 0 então o dados está vazio
        if dados.count() == 0:
            # lê o arquivo .csv que está na pasta data
            with open('data/uf.csv') as ficheiro:
                reader = csv.reader(ficheiro)
                for linha in reader:
                    estado = {
                        "estado_id": linha[0],
                        "estado_uf": linha[1],
                        "estado": linha[2]
                    }
                    estado_list.append(estado)
            
            # Insere as informações na collection
            estados.insert_many(estado_list)
            estado_list = []
            
            # Procura no database os dados inseridos e já os lista
            dadosCriados = estados.find({}, {'_id': False})
            for dado in dados:
                estado_list.append(dado)
            self.ResponseWithJson(1,estado_list)
        else:
            for dado in dados:
                estado_list.append(dado)
            self.ResponseWithJson(1,estado_list)

class allCidades(DefaultHandler):
    def get(self,uf):
        if len(uf) == 2:
            # Tudo que vier no uf passa pelo upper() -> tudo maiúsculo
            ufUpper = uf.upper()
            
            # {"_id": False} nega o dado "_id" de vir junto com as outras informações
            dados = cidades.find({"estado_uf": ufUpper}, {"_id": False})
            cidade_list = []
            if dados.count() == 0:
                # lê o arquivo .csv que está na pasta data
                with open('data/cidades.csv') as ficheiro:
                    reader = csv.reader(ficheiro)
                    
                    # lê cada linha do arquivo
                    for linha in reader:
                        cidade = {
                            "cidade_ibge": linha[0],
                            "estado_uf": linha[1],
                            "cidade_nome": linha[2]
                        }
                        cidade_list.append(cidade)
                
                # Insere as informações na collection
                cidades.insert_many(cidade_list)
                cidade_list = []
                
                # e depois ja faz um find para listar na tela as informações
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
    def get(self,cep_param):
        try:
            # Procura pelo cep desejado, se der qualquer erro nessa linha já vai para o except
            endereco = pycep_correios.consultar_cep(cep_param)

            # Procura pelo cep desejado no database
            cep = ceps.find_one({"cep": endereco["cep"]}, {"_id": False})

            # Se não encontrar, já insere e lista
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