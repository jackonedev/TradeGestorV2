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
        try:
            with open('contratos/{}.txt'.format(ingreso.upper()),'r') as f:
                f.read()
            return ingreso.upper()
            pass
        except:
            pass
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