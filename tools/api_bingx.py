import os
from dotenv import load_dotenv
import requests
import time
from http.client import HTTPException
import hmac
import hashlib


load_dotenv()

API_KEY = os.environ['API_KEY'] 
SECRET_KEY = os.environ['SECRET_KEY'] 

URL = 'https://open-api.bingx.com'

BINGX_ERRORS = {
    100001: "signature verification failed",
    100500: "Internal system error",
    80001: "request failed",
    80012: "service unavailable",
    80014: "Invalid parameter",
    80016: "Order does not exist",
    80017: "position does not exist"
}

services = {'GET_1':'/openApi/swap/v2/quote/contracts',
            'GET_2':'/openApi/swap/v2/user/balance',
            'GET_3':'/openApi/swap/v2/quote/price',
}


def generate_signature(secret_key, query_params):
    """Generar firma encriptada"""
    signature = hmac.new(
        key = secret_key.encode('utf-8'), 
        msg = query_params.encode('utf-8'), 
        digestmod = hashlib.sha256
        ).hexdigest()
    return signature

def api_request(service, method='GET', query_params=None, sign=False):
    """docstring"""
    ROOT_URL = URL
    url = f'{ROOT_URL}{service}'
    header = {#TODO: header only if user set his API key
        'Content-Type': 'application/json',
        'X-BX-APIKEY': API_KEY,
    }

    timestamp = int(time.time() *1000)
    params = f'timestamp={timestamp}'
    if query_params:
        params += f'&{query_params}'
    if sign:
        signature = generate_signature(SECRET_KEY, params)
        params += f'&signature={signature}'
    
    url += f'?{params}'
    if method == 'GET':
        response = requests.get(url, headers=header)
    else:
        response = requests.post(url, headers=header)

    if response.status_code != 200:
        print (f'status_code: {response.status_code}')
        print (f'message: {response.text}')
        raise HTTPException()

    response = response.json()
    if 'success' in response and not response.get('success'):
        print ('status_code=400')
        print (f'detail={BINGX_ERRORS.get(response.get("code"))}')
        raise HTTPException()

    return response


def actualizar_contratos():
    """Se conecta a la API de BingX y descarga todos los contratos futuros disponibles en el disco local"""
    contracts = api_request(services['GET_1'])
    data = contracts['data']
    for i in range(len(data)):
        name_asset = contracts['data'][i]['asset']
        with open(f'contratos/{name_asset}.txt', 'w') as f:
            f.write(str(data[i]))
    
def cargar_contrato(par):
    name_contract = list(filter(lambda x: x.startswith(par.upper()), os.listdir('contratos')))[0]
    with open(f'contratos/{name_contract}', 'r') as f:
        contract = eval(f.read())
    return contract
    