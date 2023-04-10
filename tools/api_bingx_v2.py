import os
from dotenv import load_dotenv
import requests
import time
import hmac
from hashlib import sha256

load_dotenv()


try:
    API_KEY = os.environ['API_KEY'] 
    SECRET_KEY = os.environ['SECRET_KEY'] 
except KeyError:
    print ('\n-NO SE ENCUENTRAN LAS CLAVES NECESARIAS-\n')
    exit()

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

def post_market_order(symbol, side, positionSide, quantity, type, price=None, stopPrice=None):
    payload = {}
    path = '/openApi/swap/v2/trade/order'
    methed = "POST"
    paramsMap = {
        "symbol": symbol,
        "side": side,
        "positionSide": positionSide,
        "quantity": quantity,
        "type": type,
        "timestamp": int(time.time() * 1000),
    }

    if type == "LIMIT":
        paramsMap["price"] = price

    elif type == 'TRIGGER_LIMIT':
        paramsMap["price"] = price
        paramsMap["stopPrice"] = price

    elif type == 'STOP_MARKET' or type == 'TAKE_PROFIT_MARKET' or type == 'TRIGGER_MARKET':
        paramsMap["stopPrice"] = stopPrice


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
    return response.text

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