import os
from dotenv import load_dotenv
import requests
import time
import hmac
from hashlib import sha256
from http.client import HTTPException

load_dotenv()


try:
    API_KEY = os.environ['API_KEY'] 
    SECRET_KEY = os.environ['SECRET_KEY'] 
except KeyError:
    print ('\n-NO SE ENCUENTRAN LAS CLAVES NECESARIAS-\n')
    exit()

URL = 'https://open-api.bingx.com'

##TODO: No recuerdo si está estipulado para que retorne el error por si algo no llegar a funcionar
BINGX_ERRORS = {
    100001: "signature verification failed",
    100500: "Internal system error",
    80001: "request failed",
    80012: "service unavailable",
    80014: "Invalid parameter",
    80016: "Order does not exist",
    80017: "position does not exist"
}

services = {'GET_1': '/openApi/swap/v2/quote/contracts',
            'GET_2': '/openApi/swap/v2/user/balance',
            'GET_3': '/openApi/swap/v2/quote/price',
            'POST_1': '/openApi/swap/v2/trade/leverage'
}



def switch_leverage(symbol, side, leverage):
    payload = {}
    path = '/openApi/swap/v2/trade/leverage'
    methed = "POST"
    paramsMap = {
        "symbol": symbol,
        "timestamp": int(time.time() * 1000),
        "side": side,
        "leverage": leverage
    }
    paramsStr = praseParam(paramsMap)
    return send_request(methed, path, paramsStr, payload)


def post_order(**kwars):
    payload = {}
    path = '/openApi/swap/v2/trade/order'
    methed = "POST"
    paramsMap = {"timestamp": int(time.time() * 1000)}
    paramsMap.update(kwars)
    paramsStr = praseParam(paramsMap)
    return send_request(methed, path, paramsStr, payload)


def get_sign(api_secret, payload):
    signature = hmac.new(api_secret.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
    return signature


def send_request(methed, path, urlpa, payload):
    url = "%s%s?%s&signature=%s" % (URL, path, urlpa, get_sign(SECRET_KEY, urlpa))
    headers = {
        'X-BX-APIKEY': API_KEY,
    }
    response = requests.request(methed, url, headers=headers, data=payload)


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


def praseParam(paramsMap):
    sortedKeys = sorted(paramsMap)
    paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
    return paramsStr



def cacel_order(orderId, symbol):
    payload = {}
    path = '/openApi/swap/v2/trade/order'
    methed = "DELETE"
    paramsMap = {
        "orderId": orderId,
        "timestamp": int(time.time() * 1000),
        "symbol": symbol,
    }
    paramsStr = praseParam(paramsMap)
    return send_request(methed, path, paramsStr, payload)


def get_balance():
    payload = {}
    path = '/openApi/swap/v2/user/balance'
    methed = "GET"
    paramsMap = {
        "timestamp": int(time.time() * 1000),
    }
    paramsStr = praseParam(paramsMap)
    return send_request(methed, path, paramsStr, payload)
