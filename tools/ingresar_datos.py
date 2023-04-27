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