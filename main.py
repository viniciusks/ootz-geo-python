# -*- coding: UTF-8 -*-
# Imports
import csv
import json
import tornado.ioloop
import tornado.web
import tornado.template
import urllib3
import requests
import pycep_correios
from pycep_correios.excecoes import CEPInvalido
from viacep import viacep
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
        # Tudo que vier no uf passa pelo upper() -> tudo maiúsculo
        ufUpper = uf.upper()
        
        if uf == "":
            # {"_id": False} nega o dado "_id" de vir junto com as outras informações
            dados = cidades.find({}, {"_id": False})
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
                dadosCriados = cidades.find({}, {"_id": False})
                for dado in dadosCriados:
                    cidade_list.append(dado)
                self.ResponseWithJson(1,cidade_list)
            else:
                for dado in dados:
                    cidade_list.append(dado)
                self.ResponseWithJson(1,cidade_list)
        elif len(uf) == 2:
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
        # COMENTÁRIO TESTE
        # Pega o type cep, para ver qual api será utilizada
        type_cep = self.get_argument("type","")
        type_cep_low = type_cep.lower()
        if type_cep == "":
            type_cep_low = "viacep"

        endereco_json = {}
        flag_insertion = False
        str1 = ""
        str2 = ""

        # Verifica se o cep não é inválido
        if len(cep_param) > 8:
            self.ResponseWithJson(0,"CEP inválido!")
            return

        if type_cep_low == "viacep":
            # Procura pelo cep desejado no database
            cep = ceps.find_one({"cep": cep_param}, {"_id": False})

            # Se não existir o cep, ele é inserido no MongoDB
            if cep is None:
                endereco = viacep.ViaCEP(cep_param)

                # Traz todas as informações do CEP que vieram do "ViaCEP()"
                data = endereco.getDadosCEP()

                # Tratamento de erro, caso o CEP não exista
                for d in data:
                    if d == "erro":
                        self.ResponseWithJson(0,"CEP inválido!")
                        return

                # Trata o CEP vindo do viacep, retira o "-" do CEP
                for i,dc in enumerate(data['cep']):
                    if i <= 4:
                        str1 += dc
                    elif i > 5:
                        str2 += dc
                    else:
                        pass
                
                # Junta as strings do CEP que antes estavam separadas
                data_cep = '{}{}'.format(str1,str2)

                # Faz um find_one nos estados referente ao cep, para trazer junto o estado por escrito
                estado = estados.find_one({"estado_uf": data['uf']}, {"_id": False})

                # Estrutura base para o MongoDB
                endereco_json = {
                    "cep": data_cep,
                    "logradouro": data['logradouro'],
                    "cidade": data['localidade'],
                    "bairro": data['bairro'],
                    "estado": estado['estado'],
                    "uf": data['uf']
                }

                # Flag para permitir a inserção do CEP dentro do MongoDB
                flag_insertion = True

            # Caso contrário apenas traz o valor dele
            else:
                endereco_json = cep

        elif type_cep_low == "pycorreios":
            # Procura pelo cep desejado no database
            cep = ceps.find_one({"cep": cep_param}, {"_id": False})

            if cep is None:
                # Procura pelo cep desejado, se der qualquer erro nessa linha já vai para o except
                try:
                    endereco = pycep_correios.consultar_cep(cep_param)
                except CEPInvalido:
                    self.ResponseWithJson(0,"CEP inválido!")
                # Faz um find_one nos estados referente ao cep, para trazer junto o estado por escrito
                estado = estados.find_one({"estado_uf": endereco['uf']}, {"_id": False})
                # Estrutura base para o MongoDB
                endereco_json = {
                    "cep": endereco['cep'],
                    "logradouro": endereco['end'],
                    "cidade": endereco['cidade'],
                    "bairro": endereco['bairro'],
                    "estado": estado['estado'],
                    "uf": endereco['uf']
                }

                # Flag para permitir a inserção do CEP dentro do MongoDB
                flag_insertion = True
            
            # Caso contrário apenas traz o valor dele
            else:
                endereco_json = cep

        # Precisa da permissão para entrar neste bloco de código
        if flag_insertion == True:
            # Inserção no MongoDB
            ceps.insert_one(endereco_json)
            endereco_json = ceps.find_one({"cep": endereco_json['cep']}, {"_id": False})
            self.ResponseWithJson(1,endereco_json)
        else:
            self.ResponseWithJson(1,endereco_json)

def make_app():
    return tornado.web.Application([
        (r"/", Home),
        (r"/estados", allEstados),
        (r"/cidades/(.*)", allCidades),
        (r"/consulta/cep/([0-9]+)", ConsultaCep),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8086)
    tornado.ioloop.IOLoop.current().start()