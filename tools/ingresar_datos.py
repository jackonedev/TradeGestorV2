from itertools import count
from collections import deque

def ingreso_bool(label):
    x_bool = count(1)
    x_bool_limit = 3  
    chance = 1
    print (label)
    print(('< 1: Si >    < 0: No >'))
    ingreso = input('>> ')
    if not (ingreso == '1' or ingreso == '0'):
        chance = next(x_bool) + 1
        print(( 'Intento {} de {}'.format(chance, x_bool_limit)))
        ingreso = input('>> ')

    if chance == x_bool_limit:
        print(( 'Intento agotados\n'))
        return
    print()
    return bool(int(ingreso))


def ingreso_bool_personalizado(op1, op2, default=None):
    x_bool = count(1)
    x_bool_limit = 3  
    chance = 1
    print(('< 1: {} >    < 0: {} >'.format(op1, op2)))
    ingreso = input('>> ')
    if default and ingreso=='':
        return default
    if not (ingreso == '1' or ingreso == '0'):
        chance = next(x_bool) + 1
        print(( 'Intento {} de {}'.format(chance, x_bool_limit)))
        ingreso = input('>> ')

    if chance == x_bool_limit:
        print(( 'Intento agotados\n'))
        return
    print()
    if ingreso == '1':
        return op1
    else:
        return op2


def ingreso_entero(label):#TODO: Decorators
    chance = count(1)
    limit = 3

    ingreso = input(label)
    while not ingreso.isdigit():
        chance = next(chance) + 1
        print(( 'Intento {} de {}'.format(chance, limit)))
        ingreso = input('Vuelva a ingresar "{}" = '.format(label))
        if chance == limit:
            print(( 'Intentos agotados\n'))
            return
    return int(ingreso)



def entero_o_porcentual(label):#TODO: si el input termina en . es porcentual -> ejemplo 3. == 3% ; 3.4. = 3.4%
    print (label)
    ingreso = input("Ingrese un numero entero o porcentual: ")
    if ingreso.count('%')==1 and ingreso.endswith('%'):
        return float(ingreso.replace('%',''))/100, True
    elif ingreso.isdigit():
        return int(ingreso), False
    else:
        try:
            return float(ingreso), False
        except:
            print(('Ingreso vacío'))#TODO BORRAR
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