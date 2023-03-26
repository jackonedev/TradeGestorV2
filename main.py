# VERSION 4 PARTE 1: Empezamos a implementar la API
import numpy as np
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
    header = {
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

# contracts = api_request(service='/openApi/swap/v2/quote/contracts', query_params='BTCUSD')
# account_balance = api_request('/openApi/swap/v2/user/balance', method='GET', sign=True)


## SEGUNDA CAPA DE LA API

def get_account_balance():
    account_balance = api_request('/openApi/swap/v2/user/balance', method='GET', sign=True)
    return np.floor(float(account_balance['data']['balance']['balance']))

def price_BTC():
    return float(api_request('/openApi/swap/v2/quote/price', query_params='symbol=BTC-USDT')['data']['price'])
def price_ETH():
    return float(api_request('/openApi/swap/v2/quote/price', query_params='symbol=ETH-USDT')['data']['price'])






## FUNCIONES DEL MAIN


def apalancamiento(precio_entrada, worst_sl, direccion_trade, price_precision):
    """
    precio_entrada / apalancamiento = distancia entre el precio de entrada y el stop loss más alejado
    Para trabajar con margen de seguridad le quitamos una unidad al apalancamiento
    """
    dist = abs(precio_entrada - worst_sl)
    apalancamiento = int(precio_entrada / dist) -2
    if direccion_trade == 'LONG':
        precio_liquidacion = precio_entrada *(1 - 1/apalancamiento)
    elif direccion_trade == 'SHORT':
        precio_liquidacion = precio_entrada *(1 + 1/apalancamiento)
    return apalancamiento, precio_liquidacion










# VERSION 4 PARTE 2.2
if __name__ == '__main__':
    from tools.ingresar_datos import ingreso_bool, ingreso_bool_personalizado, entero_o_porcentual
    from itertools import count

    contract = {'contractId': '100',
        'symbol': 'BTC-USDT',
        'size': '0.0001',
        'quantityPrecision': 4,
        'pricePrecision': 1,
        'feeRate': 0.0005,
        'tradeMinLimit': 1,
        'maxLongLeverage': 150,
        'maxShortLeverage': 150,
        'currency': 'USDT',
        'asset': 'BTC',
        'status': 1
    }
    qty_precision = contract['quantityPrecision']
    price_precision = contract['pricePrecision']

    print ('''
    ============================================================
            BIENVENIDO A LA MEJOR CALCULADORA DE RIESGO
    ============================================================
TradeGestorDEMO v2
Exchange: BingX
Cuenta: Future Perpetual
Par: BTC-USDT

    ''')




    vol_cta = get_account_balance()
    riesgo_posicion = 5#%
    print ('Direccion del trade:')
    direccion_trade = ingreso_bool_personalizado('LONG', 'SHORT')
    n_entradas = 1
    if n_entradas <= 0 or n_entradas > 5:
        raise ValueError('La posición solo admite hasta 5 entradas')

    # CALCULO DE LA POSICION
    # vol_cta *= 10 #  <-- preapalancamiento
    vol_operacion = vol_cta * riesgo_posicion /100
    vol_entrada = vol_operacion / n_entradas

    print ("""
>>    DATOS DE LA CUENTA
        - volumen cuenta  = {}

>>    DATOS DE LA POSICION
        - riesgo posicion = {}%
        - direccion trade = {}
        - nº entradas = {}
        - volumen operacion = {}
        - volumen por entrada = {}

        """.format(vol_cta, riesgo_posicion, direccion_trade, n_entradas, vol_operacion, vol_entrada))


    print ('''
    ============================================================
                    MODULO DE DIVERSIFICACION
    ============================================================
    
    ''')
    estado_entradas = []
    for i in range(n_entradas):
        estado_entradas.append(ingreso_bool(f'Colocar entrada {i+1}?'))
    print (f'Entradas COLOCADAS: {sum(estado_entradas)}  |  Entradas ANULADAS: {len(estado_entradas)-sum(estado_entradas)}')


    target_entradas = []
    print ('\nCargando precio...')
    benchmark = price_BTC()
    print ('continuando\n')
    display_estado = """

    ============================================================
                            ENTRADA Nº {}
    ============================================================
    precio BTC de referencia = {}
    """
    entrada_count = count(1)
    for estado in estado_entradas:
        if estado:
            print (display_estado.format(next(entrada_count), benchmark))
            entrada = ingreso_bool_personalizado('MARKET', 'LIMIT', default='MARKET')
            if entrada == 'LIMIT':
                entrada, pct = entero_o_porcentual('>>  Ingrese PRECIO DE ENTRADA: ')
                if pct and direccion_trade=='LONG':
                    entrada = benchmark *(1-entrada)
                elif pct and direccion_trade=='SHORT':
                    entrada = benchmark *(1+entrada)
                elif not entrada:
                    raise ValueError('No se puede ingresar un orden LIMIT sin precio entrada')
            elif entrada == 'MARKET':
                entrada = benchmark
            else:
                raise ValueError('No se puede colocar una entrada vacia')

            sl, pct = entero_o_porcentual('>>  Ingrese target STOPLOSS: ')
            if pct and direccion_trade=='LONG':
                sl = benchmark * (1 - sl)
            elif pct and direccion_trade=='SHORT':
                sl = benchmark * (1 + sl)
            elif not sl:
                raise ValueError('No se puede puede ingresar una orden LIMIT sin target StopLoss')

            target_entradas.append((entrada, sl))

            for entrada, sl in target_entradas:
                if direccion_trade == 'LONG':
                    if entrada <= sl:
                        raise ValueError('En un trade LONG, la entrada no puede ser menor que el StopLoss')
                elif direccion_trade == 'SHORT':
                    if entrada >= sl:
                        raise ValueError('En un trade SHORT, la entrada no puede ser mayor que el StopLoss')


    # DIMENSIONAMIENTO DEL TRADE
    #1. promediar entradas
    entradas = [entrada for entrada, _ in target_entradas]
    entrada_promedio = np.mean(entradas)
    #2. Obtener el stop loss más alejado
    sls = [sl for _, sl in target_entradas]
    if direccion_trade == 'LONG':
        worst_sl = np.min(sls)
    elif direccion_trade == 'SHORT':
        worst_sl = np.max(sls)
    #3. medir el apalancamiento para estar lo más cerca posible del stop loss más alejado, con un margen hardcoded de 2
    apal_x, precio_liq = apalancamiento(entrada_promedio, worst_sl, direccion_trade, price_precision)

    qty_entradas = [vol_entrada / entrada_i * apal_x for entrada_i in entradas]

    # IMPRESION DE RESULTADOS
    print (f"""
    RESULTADOS TRADE {direccion_trade}
        Benchmark = {benchmark}
        Entrada promedio = {round(entrada_promedio, price_precision)}
        StopLoss más alejado = {round(worst_sl, price_precision)}
        Apalancamiento = {apal_x}
        Precio de liquidación = {round(precio_liq, price_precision)}
        Cantidad de entradas = {[round(qty_e, qty_precision) for qty_e in qty_entradas]}
        """)

    import sys
    sys.exit(0)

    ## EJECUCION DE LA POSICION
    def ejecutar():
        """
        Función que ejecuta el trade
        """
        if input('Ejecutar?: '):
            print('Ejecutando...')
            return True
        else:
            print('Entrada pendiente')
            return False

    for entrada in target_entradas:
        if ejecutar():
            print('Entrada ejecutada')
        else:
            print('Entrada pendiente')
