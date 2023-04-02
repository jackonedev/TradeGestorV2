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