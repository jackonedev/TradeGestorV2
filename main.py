#  VERSION 6

import numpy as np
import pandas as pd
import os
from dotenv import load_dotenv
import requests
import time
from http.client import HTTPException
import hmac
import hashlib
from rich.console import Console
from rich.table import Table
from datetime import datetime
import locale
import codecs



locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")

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
def price_XRP():
    return float(api_request('/openApi/swap/v2/quote/price', query_params='symbol=XRP-USDT')['data']['price'])






## FUNCIONES DEL MAIN


def apalancamiento(precio_entrada, worst_sl, direccion_trade):
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

def generar_rows(n_entradas, estado_entradas, entradas, sls, qty_entradas):
    id = [str(i) for i in range(1, n_entradas+1)]
    estado_entradas = ['Calculada' if e else 'Omitida' for e in estado_entradas]
    entradas = [entradas[i] if i < len(entradas) else 0.0 for i in range(n_entradas)]
    sls = [sls[i] if i < len(sls) else 0.0 for i in range(n_entradas)]
    qty_entradas = [qty_entradas[i] if i < len(qty_entradas) else 0.0 for i in range(n_entradas)]
    riesgo = [abs(entradas[i] - sls[i])*qty_entradas[i] for i in range(n_entradas)]

    entradas = [str(round(elemento, price_precision))for elemento in entradas]
    sls = [str(round(elemento, price_precision))for elemento in sls]
    qty_entradas = [str(round(elemento, qty_precision))for elemento in qty_entradas]
    riesgo = [str(round(elemento, 1))for elemento in riesgo]
    return id, estado_entradas, entradas, sls, qty_entradas, riesgo



################################################################################################
################################################################################################
################################################################################################
#########################              PROGRAMA PRINCIPAL              #########################
################################################################################################
################################################################################################
################################################################################################


if __name__ == '__main__':
    from tools.ingresar_datos import ingreso_bool, ingreso_bool_personalizado, entero_o_porcentual
    from tools.app_modules import cargar_contrato
    from itertools import count

    print ('''
    ============================================================
            BIENVENIDO A LA MEJOR CALCULADORA DE RIESGO
    ============================================================
TradeGestorDEMO v2
Exchange: BingX
Cuenta: Future Perpetual
Pares: BTC-USDT  |  XRP-USDT

    ''')


    # SETEO DE LAS VARIABLES INICIALES
    print ('Seleccione par a operar:')
    par = ingreso_bool_personalizado('BTC', 'XRP')
    print ('Obteniendo datos del contrato...')
    if not par:
        exit()
    contract = cargar_contrato(par)
    qty_precision = contract['quantityPrecision']
    price_precision = contract['pricePrecision']

    ## ESTABLECER EL APALANCAMIENTO MAXIMO DEL PAR (OBTENIDO MANUALMENTE INGRESANDO A LA PLATFORMA)#TODO: exportar esta data a un archivo externo
    if par == 'BTC':
        apalancamiento_maximo = 150
    elif par == 'XRP':
        apalancamiento_maximo = 125





    print ('Obteniendo datos de la cuenta...\n')
    # vol_cta = get_account_balance()#TODO: VERSION USERLESS
    vol_cta = 1000#TODO: VERSION USERLESS
    riesgo_posicion = 5#%
    print ('Direccion del trade:')
    direccion_trade = ingreso_bool_personalizado('LONG', 'SHORT')
    n_entradas = 5
    if n_entradas <= 0 or n_entradas > 5:
        raise ValueError('La posición solo admite hasta 5 entradas')

    # CALCULO DE LA POSICION
    vol_operacion = vol_cta * riesgo_posicion /100
    vol_entrada = vol_operacion / n_entradas

    display_data_inicial = """
>>    DATOS DE LA CUENTA
        - volumen cuenta  = {}

>>    DATOS DE LA POSICION
        - par = {}
        - riesgo posicion = {}%
        - direccion trade = {}
        - nº entradas = {}
        - volumen operacion = {}
        - volumen por entrada = {}

        """.format(vol_cta, par, riesgo_posicion, direccion_trade, n_entradas, vol_operacion, round(vol_entrada,2))
    print (display_data_inicial)

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
    if par == 'BTC':
        benchmark = price_BTC()
    elif par == 'XRP':
        benchmark = price_XRP()
    print ('continuando\n')
    display_estado = """

    ============================================================
                            ENTRADA Nº {}
    ============================================================
    Precio de referencia {} = {}
    """
    entrada_count = count(1)
    for estado in estado_entradas:
        if estado:
            print (display_estado.format(next(entrada_count), par, benchmark))
            # DETERMINACION DE LA ENTRADA
            entrada = ingreso_bool_personalizado('MARKET', 'LIMIT', default='MARKET')
            if entrada == 'LIMIT':
                entrada, pct = entero_o_porcentual('>>  PRECIO DE ENTRADA (Vacío significa precio MARKET) ')
                if pct and direccion_trade=='LONG':
                    entrada = benchmark *(1-entrada)
                elif pct and direccion_trade=='SHORT':
                    entrada = benchmark *(1+entrada)
                elif not entrada:
                    print ('Ingresando orden LIMIT a precio MARKET')
                    entrada = benchmark
                    # raise ValueError('No se puede ingresar un orden LIMIT sin precio entrada')
            elif entrada == 'MARKET':
                entrada = benchmark
            else:
                raise ValueError('No se puede colocar una entrada vacia')
            # DETERMINACION DEL STOPLOSS
            sl, pct = entero_o_porcentual('>>  STOPLOSS ')
            if pct and direccion_trade=='LONG':
                sl = benchmark * (1 - sl)
            elif pct and direccion_trade=='SHORT':
                sl = benchmark * (1 + sl)
            elif not sl:#TODO meter la SL dentro de un bucle while o agregar la función de chance
                raise ValueError('No se puede puede ingresar una orden LIMIT sin target StopLoss')

            target_entradas.append((entrada, sl))
            # VERIFICACION
            for entrada, sl in target_entradas:
                if direccion_trade == 'LONG':
                    if entrada <= sl:
                        raise ValueError('En un trade LONG, la entrada no puede ser menor que el StopLoss')
                elif direccion_trade == 'SHORT':
                    if entrada >= sl:
                        raise ValueError('En un trade SHORT, la entrada no puede ser mayor que el StopLoss')


    # DIMENSIONAMIENTO DEL TRADE
    print ('\nCalculando posición...')
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
    apal_x, precio_liq = apalancamiento(entrada_promedio, worst_sl, direccion_trade)

    if apal_x > apalancamiento_maximo:
        raise ValueError(f'El apalancamiento máximo para este par es de {apalancamiento_maximo}x\nEl apalancamiento calculado es de {apal_x}x')

    qty_entradas = [round(vol_entrada/abs(x[0] - x[1]),qty_precision) for x in target_entradas]




    display_resultado = """
    
    ============================================================
                            RESULTADOS
    ============================================================
    
    """


    # IMPRESION DE DESCRIPCION DE TRADE
    display_resultados =f"""
>>  DESCRIPCION TRADE {direccion_trade}
        - Precio de referencia = {benchmark}
        - Entrada promedio = {round(entrada_promedio, price_precision)}
        - StopLoss más alejado = {round(worst_sl, price_precision)}
        - Apalancamiento = {apal_x}
        - Precio de liquidación = {round(precio_liq, price_precision)}
        - Total comerciado = {sum([round(qty_e, qty_precision) for qty_e in qty_entradas])}
        - Pérdidas peor escenario = {round(sum([abs(entradas[i] - sls[i])*qty_entradas[i] for i in range(sum(estado_entradas))]), 2)}
        """
    print (display_resultados)

    # GENERACION DE TABLA DE RESUMEN DE ENTRADAS
    console = Console(record=True)
    table = Table(title="RESUMEN ENTRADAS: {} | PAR: {}".format(direccion_trade, par))

    table.add_column("Nº", justify="right", style="cyan", no_wrap=True)
    table.add_column("CONDICION", style="cyan")
    table.add_column("ENTRADA", justify="right", style="cyan")
    table.add_column("STOPLOSS", justify="right", style="cyan")
    table.add_column("CANTIDAD", justify="right", style="cyan")
    table.add_column("RIESGO", justify="right", style="cyan")



    row_1, row_2, row_3, row_4, row_5, row_6 = generar_rows(n_entradas, estado_entradas, entradas, sls, qty_entradas)

    for i in range(n_entradas):
        table.add_row(row_1[i], row_2[i], row_3[i], row_4[i], row_5[i], row_6[i])
    console.print(table)
    


    ######      ######      ######
    ##  GUARDAR POSICION EN TXT
    ######      ######      ######

    # CREAR CARPETA
    path = os.path.join(os.getcwd(), 'registro')
    os.makedirs(path, exist_ok=True)

    # OBTENER DATA DE HOY
    fecha_actual = datetime.now()
    nombre_mes = fecha_actual.strftime("%B").title()
    hora = '\n\n\nTrade calculado el día {} a las {}'.format(fecha_actual.strftime("%d de {mes} de %Y").format(mes=nombre_mes), fecha_actual.strftime("%H:%M:%S"))
    
    # LEEMOS EL NOMBRE DE LOS FICHEROS DEL DIRECTORIO CREADO
    file_names = os.listdir(path=path)

    # SI LA LISTA ESTA VACIA CREAR EL PRIMER ARCHIVO
    if len(file_names) == 0:
        file_name = f'01_{direccion_trade}_{par}_{fecha_actual.strftime("%d_{}").format(nombre_mes)}.txt'

    # SI LA LISTA NO ESTA VACIA OBTENER EL ULTIMO ARCHIVO Y LEER EL CONTADOR
    else:
        last_file = file_names[-1]
        i = int(last_file.split('_')[0])
        file_name = f'{i+1:02d}_{direccion_trade}_{par}_{fecha_actual.strftime("%d_{}").format(nombre_mes)}.txt'


    file = os.path.join(path, file_name)


    with codecs.open(file, 'w', encoding='utf-8') as f:
        f.write('TradeGestorDEMO: v2 \nCalculadora de riesgo y gestor de posiciones\nExchange: BingX\n')
        f.write(display_data_inicial)
        f.write(display_resultados)
        f.write('\n\n\n')
        f.write(console.export_text())
        f.write(hora)
        f.write('\n   -- Desarrollado por Jackone Action Software Company\n   -- jackone.action.software@gmail.com')


    ### OBTENEER LOS VALORES DEL RESULTADO INDIVIDUAL DE LAS ENTRADAS Y DEL TRADE EN GENERAL

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
