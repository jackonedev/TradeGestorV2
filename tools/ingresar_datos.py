from itertools import count

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



def entero_o_porcentual(label):
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




def ingresar_cifra(label):
    """
=============
CONVENCION 1
1- si la cifra tiene un "." y comienza con un numero mayor a 0 y menor que 100, y tiene 3 digitos despues del "."
entonces la cifra es un numero.

Si en vez de tener 3 digitos, posee otra cantidad
entonces la cifra es un porcentaje

Ejemplo:
  
Cifras Monetarias:   25.500; 1.150; 4.755   <-- (siempre terminan con 3 digitos)
Cifras Porcentuales: 25.5;   1.15;  4.7555

Para ingresar cifras porcentuales con 3 digitos decimales utilice el caracter "%"
=============

=============
CONVENCION 2
Todas las CIFRA MONETARIA se expresan en VALORES ENTEROS, y todas las CIFRA PORCENTUAL en VALORES DECIMALES.
=============


Se ingresa por pantalla una variable y retorna una tupla(bool, int or float)
Si return es (True, ) el segundo elemento es float
Si return es (False, ) el segundo elemento es int

bool sirve para identificar si el valor es determinado o requiere posterior procesamiento.
Si bool = True, requiere procesamiento
Si bool = False, valor determinado


posibles variantes de entradas de test:
        primera condicion
        - 550000
        - 20
        segunda condicion:
        - 2.200.000
        - 550.000
        - 20.57
        - 0.2
        - 0.21
        tercera condicion:
        - 20%
        - 20.6%
        - 20.57%
        cuarta condicion:
        - 550.000,0
        - 0,2
        - 20,0%
    """

    global cifra, contador_secundario_numerico


    print( '{}) Provea "{}" - ingrese porcentaje o monto total'.format(next(contador_secundario_numerico), label))
    print( 'Ejemplo: 500.000 | ejemplo: 20% | ejemplo: 0.197')
    

    cifra = input('declaro = ')
    if cifra.replace(",","") == cifra:
        if cifra.isdigit():
            if int(cifra) > 100:
                print(( '1- cifra expresada monetariamente'))
                return False, int(cifra)
            elif 0 <= int(cifra) <= 100:
                print(( '1- cifra expresada porcentualmente'))
                return True, float(cifra)/100
            else:
                print(( '1- primera condicion fallida'))
                return False, None
        elif cifra.replace(".","").isdigit():
            if cifra.count('.') > 1:
                print(( '2- cifra expresada monetariamente'))
                return False, int(cifra.replace(".",""))
            if int(float(cifra)) >= 100:
                print(( '2- cifra expresada monetariamente'))
                return False, int(cifra.replace(".",""))
            elif 0 < int(float(cifra)) < 100:
                if len(cifra.split('.')[-1]) == 3:
                    print(( '2- cifra expresada monetariamente'))
                    return False, int(cifra.replace(".",""))
                else:
                    print(( '2- cifra expresada de forma porcentual'))
                    return True, float(cifra)/100
            elif int(float(cifra)) == 0:
                print(( '2- cifra expresada de forma porcentual'))
                return True, float(cifra)
            else:
                print(( '2- segunda condicion fallida'))
                return False, None
        elif cifra.replace(".","").replace("%","").isdigit():
            cifraux = cifra.replace(".","").replace("%","")
            if cifraux.count('.') == 0 and 0 <= int(cifraux) <= 100:
                #ERROR: 0.2% -> 0.02
                print(( '3- cifra expresada de forma porcentual sin decimales'))
                return True, float(cifraux)/100
            elif len(cifraux) > 2:
                print(( '3- cifra expresada de forma porcentual con decimales'))
                return True, float(cifra.replace('%',''))/100#TODO: toma como valor aceptable 101%
            else:
                print(( '3- tercera condicion fallida'))
                return False, None         
        else:
            print(( 'error etapa 1'))
            return False, None
    elif cifra.count(',') > 0:
        if cifra.count(',') > 1:
            return 'No entiendo el numero'
        else:
            if cifra.replace(',','').isdigit(): 
                cifraux = cifra.replace(",",".")
                if int(float(cifraux)) > 0:
                    if int(float(cifraux)) > 1000:
                        print(( '4- cifra expresada de forma monetaria'))
                        return False, int(float(cifraux))
                    elif 0 < int(float(cifraux)) < 100:
                        print(( '4- cifra expresada de forma porcentual entre 0 y 100'))
                        return True, float(cifraux)/100
                elif int(float(cifraux)) == 0:
                    print(( '4- cifra expresada de forma porcentual'))
                    return True, float(cifraux)
                else:
                    print(( '4- cuarta condicion fallida'))
                    return False, None
            elif cifra.replace(',','').replace('.','').isdigit():
                cifraux = cifra.replace('.','').replace(',','.')
                if int(float(cifraux)) > 0:
                    print(( '5- cifra expresada de forma monetaria'))
                    return False, int(float(cifraux))
                elif int(float(cifraux)) == 0:
                    print(( '5- cifra expresada de forma porcentual'))
                    return True, float(cifraux)/100
                else:
                    print(( '5- quinta condicion fallida'))
                    return False, None
            elif cifra.replace(',','').replace('.','').replace('%','').isdigit():
                cifraux = cifra.replace('.','').replace(',','.').replace('%','')
                if int(float(cifraux)) > 0:
                    if int(float(cifraux)) > 100:
                        print(( '6- No tiene logica un numero tan grande con el valor %'))
                    elif 0 < int(float(cifraux)) <= 100:
                        print(( '6- cifra expresada de forma porcentual entre 0 y 100'))
                        return True, float(cifraux)/100
                elif int(float(cifraux)) == 0:
                    print(( '6- cifra expreado de forma porcentual'))
                    return True, float(cifraux)
                else:
                    print(( '6- sexta condicion fallida'))
                    return False, None
            else:
                print(( 'error etapa 2'))


def ingresar_agno():
    global agno, contador_secundario_numerico
    print( '{}) Provea "plazo en años" - un numero entero'.format(next(contador_secundario_numerico)))
    agno = input('Declarar plazo en años = ')
    if not agno:
        print( 'return')
        return
    if agno.isdigit():
        if 1 <= int(agno) < 90:
            return int(agno)
        else:
            print( ('No entiendo el numero'))
            return
    else:
        print( ('No entiendo el numero'))
        return

def ingresar_tasa():
    global tasa, contador_secundario_numerico
    
    print( '{}) Provea "tasa porcentual" - numero entre 0 y 1 o entre 1 y 100'.format(next(contador_secundario_numerico)))
    tasa = input('declare = ')
    if not tasa:
        print( 'return')
        return
    if tasa.count('%') != 0:
        print( 'No se acepta el caracter "%"')
        return
    if tasa.isdigit():
        if 1 < int(tasa) < 100:
            print( '1-')
            return float(tasa)
        else:
            print( '1- error')
            return
    elif tasa.replace(',','').isdigit() and tasa.count(',') == 1:
        if int(float(tasa.replace(',','.'))) == 0:
            print( '2-')
            return float(tasa.replace(',','.')) *100
        else:
            print( '2- error')
            return
    elif tasa.replace('.','').isdigit() and tasa.count('.') == 1:

        if int(float(tasa)) == 0:
            print( '3-')
            return float(tasa) *100
        
        elif 0 < int(float(tasa)) < 100:
            print( '3-')
            return float(tasa)

        else:
            print( '3- error')
            return
    else:
        print( 'tasa- error')
        return
























