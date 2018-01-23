# ViaCEP em Python

[![PyPI version](https://badge.fury.io/py/viacep-python.svg?1.1.0)](https://pypi.python.org/pypi/viacep/1.1.0)
[![Build Status](https://travis-ci.org/leogregianin/viacep-python.svg)](https://travis-ci.org/leogregianin/viacep-python)
[![codecov](https://codecov.io/gh/leogregianin/viacep-python/branch/master/graph/badge.svg)](https://codecov.io/gh/leogregianin/viacep-python)

Buscar informações do CEP com o webservice do site http://www.viacep.com.br

## Pré requisitos

  * Instalação de qualquer versão do Python (http://www.python.org/download)
  
## Instalação das dependências

```bash
$ pip install -r requirements.txt
```

## Utilização

```bash
>>> import viacep
>>> d = viacep.ViaCEP('78048000')
>>> data = d.getDadosCEP()
>>> data
{'cep': '78048-000', 'logradouro': 'Avenida Miguel Sutil', 'complemento': 'de 5686 a 6588 - lado par', 'bairro': 'Alvorada', 'localidade': 'Cuiabá', 'uf': 'MT', 'unidade': '', 'ibge': '5103403', 'gia': ''}
>>> data['localidade']
'Cuiabá'
>>> data['uf']
'MT'
>>>
```

## Exemplo com Python Flask

* https://github.com/leogregianin/viacep-flask
* https://viacep-flask.herokuapp.com

Licença
-------
[Licença MIT](LICENSE)
