from functools import reduce
import os
from dotenv import load_dotenv



load_dotenv()



def productoria(lista):
    return reduce(lambda x, y: x*y, lista)


def calculo_operatoria(cuenta):
    try:
        vol_op = cuenta['vol_cta'] * cuenta['riesgo_op'] /100
        vol_unidad = vol_op / cuenta['n_entradas']
        1/vol_op
        return vol_op, vol_unidad
    except:
        return 0, 0



def comprobar_apis():
    try:
        API_KEY = os.environ['API_KEY'] 
        SECRET_KEY = os.environ['SECRET_KEY']
        return True
    except KeyError:
        return False
    


def imprimir_cuenta(nombre, cuenta):
    print (f'\nLa cuenta {nombre}')
    for key, value in cuenta.items():
        if key == 'vol_op' or key == 'vol_unidad':
            print ('{}: {:.2f}'.format(key, value))
        else:
            print ('{}: {}'.format(key, value))


def cargar_contrato(par):
    """Se carga desde los contratos guardados localmente"""
    path = os.path.join(os.getcwd(), 'contratos')
    if not os.path.exists(path):
        os.mkdir(path)
    name_contract = list(filter(lambda x: x.startswith(par.upper()), os.listdir('contratos')))
    if len(name_contract) == 0:
        print ('No existen contratos almacenados en el directorio')
        return
    name_contract = name_contract[0]
    path = os.path.join(os.getcwd(), 'contratos', name_contract)
    with open(path, 'r') as f:
        contract = eval(f.read())
    return contract


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


def generar_rows(n_entradas, estado_entradas, ordenes, entradas, sls, qty_entradas, price_precision, qty_precision):
    """Devuelve una lista para completar las tabla de resultados, completando los elementos que no fueron calculados"""
    id = [str(i) for i in range(1, n_entradas+1)]
    estado_entradas = ['Calculada' if e else 'Omitida' for e in estado_entradas]
    ordenes = [orden if orden else '' for orden in ordenes]
    entradas = [entradas[i] if i < len(entradas) else 0.0 for i in range(n_entradas)]
    sls = [sls[i] if i < len(sls) else 0.0 for i in range(n_entradas)]
    qty_entradas = [qty_entradas[i] if i < len(qty_entradas) else 0.0 for i in range(n_entradas)]
    riesgo = [abs(entradas[i] - sls[i])*qty_entradas[i] for i in range(n_entradas)]

    entradas = [str(round(elemento, price_precision))for elemento in entradas]
    sls = [str(round(elemento, price_precision))for elemento in sls]
    qty_entradas = [str(round(elemento, qty_precision))for elemento in qty_entradas]
    riesgo = [str(round(elemento, 1))for elemento in riesgo]
    return id, estado_entradas, ordenes, entradas, sls, qty_entradas, riesgo


def obtener_sl(entrada:float, sl:float, pct:bool, direccion_trade:str) -> float:
    if pct and direccion_trade=='LONG':
        sl = entrada * (1 - sl)
    elif pct and direccion_trade=='SHORT':
        sl = entrada * (1 + sl)
    return sl

def crear_directorio(nombre):
    path = os.path.join(os.getcwd(), nombre)
    if not os.path.exists(path):
        os.mkdir(path)