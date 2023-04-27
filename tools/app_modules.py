from functools import reduce
import os
from dotenv import load_dotenv
# from plyer import notification#DESHABILITADO PARA MAC
import pandas as pd

load_dotenv()


### FUNCIONES APP_MODULES (ORIGINAL)
### FUNCIONES APP_MODULES (ORIGINAL)
### FUNCIONES APP_MODULES (ORIGINAL)

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
            print ('{}: {:.2f} USDT'.format(key, value))
        elif key == 'riesgo_op':
            print('{}: {} %'.format(key, value))
        elif key == 'n_entradas':
            print('{}: {}'.format(key, value))
        else:
            print ('{}: {} USDT'.format(key, value))


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
    Para trabajar con margen de seguridad le quitamos una unidad al apalancamiento
    """
    apalancamiento = obtener_apalancamiento(precio_entrada, worst_sl) - 2
    precio_liquidacion = calcular_precio_liquidacion(apalancamiento, precio_entrada, direccion_trade)
    return apalancamiento, precio_liquidacion


def obtener_apalancamiento(precio_entrada, worst_sl, adj_factor=0.1):
    delta = abs(1 - precio_entrada/worst_sl)
    return int((1-adj_factor)/delta)

def variacion_precio(apal, adj_factor=0.1):
    return (1/apal) * (1-adj_factor)

def calcular_precio_liquidacion(apalancamiento, precio_entrada, direccion_trade):
    """
    Obtener precio de liquidación en función de un apalancamiento dado
    """
    distancia = precio_entrada * variacion_precio(apalancamiento)
    if direccion_trade == 'LONG':
        # precio_liquidacion = precio_entrada *(1 - 1/float(apalancamiento))
        precio_liquidacion = precio_entrada - distancia
    elif direccion_trade == 'SHORT':
        # precio_liquidacion = precio_entrada *(1 + 1/float(apalancamiento))
        precio_liquidacion = precio_entrada + distancia
    return precio_liquidacion


def generar_rows(n_entradas, estado_entradas, ordenes, entradas, sls, qty_entradas, price_precision, qty_precision):
    """Devuelve una lista para completar las tabla de resultados, completando los elementos que no fueron calculados"""
    id = [str(i) for i in range(1, n_entradas+1)]
    estado_entradas = ['Calculada' if e else 'Omitida' for e in estado_entradas]
    ordenes = [ordenes[i] if i<len(ordenes) else '' for i in range(n_entradas)]
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

#INHABILITADO PARA MAC
# def alerta(titulo, mensaje):
#     notification.notify(
#         title = titulo,
#         message = mensaje,
#         app_icon = None,
#         timeout = 5,
#         toast = False
#     )

def alerta(titulo, mensaje):
    pass


def ultimas_ordenes(path='ordenes', ultimas=5):
    files = os.listdir(path)
    print ('ULTIMAS ORDENES:')
    posible_files = []
    for file in files:
        if not file.split('_')[0].isdigit():
            continue
        posible_files.append(file)
    for file in posible_files[-ultimas:]:
        print (file)
    print ('SELECCIONA el número de orden que quieres operar: \ndefault={}'.format(pd.Series(posible_files).max()))
    return posible_files


def seleccionar_orden(posible_files):
    ingreso = input('>> ')
    if ingreso == '':
        return pd.Series([int(num.split('_')[0]) for num in posible_files]).max()
    elif ingreso.isdigit():
        if ingreso[0] == '0':
            ingreso=ingreso[1:]
        if int(ingreso) > len(posible_files):
            print ('error')
            return seleccionar_orden(posible_files)
        return int(ingreso)
    else:
        print ('error')
        exit()

def buscar_orden(num_orden, posible_files):
    for file in posible_files:
        if int(file.split('_')[0]) == num_orden:
            return file
    print ('error')
    exit()


def leer_orden(file):
    path = os.path.join(os.getcwd(), 'ordenes', file)
    with open(path, 'r') as f:
        direccion_trade = f.readline().strip()
        contrato = eval(f.readline().strip())
        target_entradas = eval(f.readline().strip())
        apalancamiento = eval(f.readline().strip())
        monto_entrada = eval(f.readline().strip())
    return direccion_trade, contrato, target_entradas, apalancamiento, monto_entrada


def verificar_fichero(par):
    "Verifica que se encuentre el fichero .txt del par la carpeta ./contratos"
    if par is None:
        return False
    path = os.path.join(os.getcwd(), 'contratos', par+'.txt')
    if not os.path.exists(path):
        print ('Por favor vaya a configuración y seleccione Descargar contratos')
        print ('Falló la operativa')
        return False
    return True



### FUNCIONES INGRESAR_DATOS (originalmente en ingresar_datos.py)

from itertools import count
from collections import deque


def diversificar_entradas(n_entradas):
    "Devuelve una lista con las entradas que debe calcular"
    if n_entradas > 1:
        print ('Indique cuales ENTRADAS desea colocar:')
        estado_entradas = []
        for i in range(n_entradas):
            estado_entradas.append(ingreso_bool(f'Colocar ENTRADA Nº {i+1}?'))
        print (f'Entradas COLOCADAS: {sum(estado_entradas)}  |  Entradas ANULADAS: {len(estado_entradas)-sum(estado_entradas)}')
        return estado_entradas
    else:
        return [True]

def ingreso_bool(label):
    MAX_TRIES = 3
    print(label)
    print('< 1: Sí >    < 0: No >')
    for i in range(MAX_TRIES):
        ingreso = input('>> ')
        if ingreso == '1':
            return True
        elif ingreso == '0':
            return False
        else:
            print('Entrada inválida. Por favor, ingrese 1 o 0.')
    print('Intentos agotados.')
    return None


def ingreso_bool_personalizado(op1, op2, default=None):
    "Esta función permite ingresar 1 o 0, o el nombre de un contrato."
    MAX_TRIES = 3  
    chance = 1
    
    print(f'< 1: {op1} >    < 0: {op2} >')
    
    while chance <= MAX_TRIES:
        ingreso = input('>> ').strip().upper()
        
        if ingreso == '':
            if default is not None:
                return default
            else:
                print('Por favor ingrese 1 o 0.')
        elif ingreso in ('1', '0'):
            if ingreso == '1':
                return op1
            else:
                return op2
        else:
            try:
                with open(f'contratos/{ingreso}.txt', 'r') as f:
                    f.read()
                return ingreso
            except FileNotFoundError:
                pass
            
            chance += 1
            if chance <= MAX_TRIES:
                print(f'Intento {chance} de {MAX_TRIES}. Por favor ingrese 1 o 0.')
    print('Intentos agotados.\n')
    


# def ingreso_bool_personalizado(op1, op2, default=None):
#     x_bool = count(1)
#     x_bool_limit = 3  
#     chance = 1
#     print(('< 1: {} >    < 0: {} >'.format(op1, op2)))
#     ingreso = input('>> ')
#     if default and ingreso=='':
#         return default
#     if not (ingreso == '1' or ingreso == '0'):
#         try:
#             with open('contratos/{}.txt'.format(ingreso.upper()),'r') as f:
#                 f.read()
#             return ingreso.upper()
#         except:
#             pass
#         chance += 1
#         print(( 'Intento {} de {}'.format(chance, x_bool_limit)))
#         ingreso = input('>> ')

#     if chance == x_bool_limit:
#         print(( 'Intento agotados\n'))
#         return
    
#     print()
#     if ingreso == '1':
#         return op1
#     else:
#         return op2


def ingreso_entero(label):#TODO: Decorators
    chance = count(1)
    limit = 3
    print (label)
    ingreso = input('>>  ')
    while not ingreso.isdigit():
        chance = next(chance) + 1
        print(( 'Intento {} de {}'.format(chance, limit)))
        ingreso = input('Vuelva a ingresar "{}" = '.format(label))
        if chance == limit:
            print(( 'Intentos agotados\n'))
            return
    return int(ingreso)



def entero_o_porcentual(label):
    print (label)
    ingreso = input(">>  ")
    if ingreso.count('%')==1 and ingreso.endswith('%'):
        return float(ingreso.replace('%',''))/100, True
    elif ingreso.isdigit():
        return float(ingreso), False
    elif ingreso.endswith('.'):
        ingreso = ingreso[:-1]
        return float(ingreso)/100, True
    else:
        try:
            return float(ingreso), False
        except:
            print()
            return None, None



def create_options_enum(opciones:list) -> list:
        opciones_input = deque(range(len(opciones)), maxlen=len(range(len(opciones))))
        opciones_input.append('0')
        opciones_input = list(opciones_input)
        return list(map(lambda x: str(x), opciones_input))
## create_options_enum(opciones) ##OK

def create_options_display(opciones: list) -> str:
        opciones_display = ''
        opciones_enum = create_options_enum(opciones)
        for i, enum in enumerate(opciones_enum):
                opciones_display += f'\t{enum}. {opciones[i]}\n'
        return opciones_display
##print(create_options_display(opciones=opciones))#OK

def create_options_dict(opciones: list) -> dict:
        opciones_dict = {}
        opciones_enum = create_options_enum(opciones)
        for i, enum in enumerate(opciones_enum):
                opciones_dict[enum] = opciones[i]
        return opciones_dict


def activate_options(opciones: list) -> str:
        """Funcion para crear menu de opciones. Se debe conocer todas las opciones de antemano y no admite valor por default"""
        print('\t\t\t>>  Opciones  <<\n')
        opciones_display = create_options_display(opciones)
        opciones_dict = create_options_dict(opciones)
        while True:
                print(opciones_display)
                opcion = input('Selecciona una opción: ')
                if opcion in opciones_dict:
                        return opciones_dict[opcion]
                else:
                        print('Opción no válida')

def ingresar_tasa():
    """Siempre devuelve un float entre 1 y 100. Si el input termina en %, se asume que es porcentual."""
    ingreso = input('>>  ')
    if not ingreso:
        print( 'return')
        return
    if ingreso.count('%') == 1 and ingreso.endswith('%'):
        ingreso = ingreso.replace('%','')
        if ingreso.isdigit():
            ingreso = float(ingreso)
            if 1 <= ingreso <= 100:
                return ingreso
            else:
                print( 'El número es demasiado grande, pruebe entre 1 y 100')
                return
        elif ingreso.replace(',','').isdigit() and ingreso.count(',') == 1 and float(ingreso.replace(',','.') <= 100):
            return float(ingreso.replace(',','.'))

        elif ingreso.replace('.','').isdigit() and ingreso.count('.') == 1 and float(ingreso) <= 100:
            return float(ingreso)
        else:
            print ('El número ingresado es demasiado grande')
            return
        
    
    if ingreso.isdigit():
        if 1 <= int(ingreso) <= 100:
            return float(ingreso)
        else:
            print( 'El número es demasiado grande, pruebe entre 1 y 100')
            return
    elif ingreso.replace(',','').isdigit() and ingreso.count(',') == 1:
        ingreso = float(ingreso.replace(',','.'))
        if ingreso < 1:
            # ej 0,3
            return ingreso *100
        elif ingreso <= 100:
            # ej 16,5
            return ingreso
        else:
            print ('El número ingresado es demasiado grande')
            return
    elif ingreso.replace('.','').isdigit() and ingreso.count('.') == 1:
        if int(float(ingreso)) == 0:
            return float(ingreso) *100
        
        elif 1 <= int(float(ingreso)) < 100:
            return float(ingreso)
        else:
            print ('El número ingresado es demasiado grande')
            return
    else:
        print( 'Ingreso no reconocido -> error')
        return                        
    


############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################

## NUEVAS FUNCIONES

def definir_entradas(estado_entradas, benchmark, direccion_trade, currency, price_precision):
    target_entradas = []
    entrada_count = count(1)
    for estado in estado_entradas:
        if estado:
            print (f'\n>>  ENTRADA Nº {next(entrada_count)}')
            # 1.7.1 Tipo de orden
            print ('Tipo de orden:')
            tipo_orden = ingreso_bool_personalizado('MARKET', 'LIMIT', default='LIMIT')
            # 1.7.2 Precio de entrada
            if tipo_orden == 'MARKET':
                entrada = benchmark
            elif tipo_orden == 'LIMIT':
                print ('Orden LIMIT | precio actual {} {}'.format(benchmark, currency))
                entrada, pct = entero_o_porcentual('Precio de ENTRADA | en blanco significa precio actual:')
                if pct and direccion_trade=='LONG':
                    entrada = benchmark *(1-entrada)
                elif pct and direccion_trade=='SHORT':
                    entrada = benchmark *(1+entrada)
                elif not entrada:
                    tipo_orden = "TRIGGER_MARKET"
                    entrada = benchmark
            else:
                print ('Falló la operativa')
                continue
            # 1.7.3 Precio de stoploss
            sl, pct = entero_o_porcentual('Indique precio de STOPLOSS:')
            chance_sl = count(1)
            sl = obtener_sl(entrada, sl, pct, direccion_trade)
            if not sl:
                print('error en la operativa- el stop loss quedó vacio')
                while next(chance_sl) < 5 and not sl:
                    sl, pct = entero_o_porcentual('Indique precio de STOPLOSS:')
                    sl = obtener_sl(entrada, sl, pct, direccion_trade)
                    if not sl:
                        print('error en la operativa- el stop loss quedó vacio')

            porcentaje_sl = round(abs(entrada - sl) / entrada * 100, 2)
            alerta(titulo=f'Orden {tipo_orden}', mensaje= f'Precio Entrada = {entrada} {currency}\nStopLoss = {sl} {currency}\nPorcentaje SL = {porcentaje_sl} %')
            target_entradas.append((round(entrada, price_precision), tipo_orden, porcentaje_sl, round(sl, price_precision)))
    return target_entradas


