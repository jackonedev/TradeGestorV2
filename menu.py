from tools.ingresar_datos import ingreso_bool_personalizado, ingresar_tasa, ingreso_entero, ingreso_bool
from tools.api_bingx import cargar_contrato, actualizar_contratos, get_account_balance
from tools.app_modules import comprobar_apis, imprimir_cuenta
online = comprobar_apis()
import os
import pickle

print ('''
    ============================================================
            BIENVENIDO A LA MEJOR CALCULADORA DE RIESGO
    ============================================================
TradeGestorDEMO v2
Exchange: BingX
Cuenta: Future Perpetual
    ''')

CUENTAS = ['online.txt', 'offline.txt', 'active.pkl']
## create path
path = os.path.join(os.getcwd(), 'cuentas')
if not os.path.exists(path):
    os.mkdir(path)
## create files for each CUENTAS
for i, cuenta in enumerate(CUENTAS):
    path = os.path.join(os.getcwd(), 'cuentas', cuenta)
    if not os.path.exists(path):
        if i == len(CUENTAS)-1:
            with open(path, 'wb') as f:
                    pickle.dump('--.. .- .-. - . -..- .--. .-. ---', f)
        else:
            with open(path, 'w') as f:
                f.write('')




while True:

    menu = """
    ============================================================
                        MENU PRINCIPAL
    ============================================================
    

\t\t\t>>  Opciones  <<

    1. Ejecutar app
    2. Configuración
    0. Salir
"""
    print(menu)
    opcion = input("Ingrese una opción: ")


    if opcion == "1":
        ## MAIN APP

        ## LECTURA DE LA CUENTA
        path = os.path.join(os.getcwd(), 'cuentas', 'active.pkl')
        with open(path, 'rb') as f:
            cuenta = pickle.load(f)
            if not isinstance(cuenta, list) and len(cuenta)==2:
                print('La cuenta activa no tiene el formato correcto')
                continue

        ##  DESEMPAQUE Y CREACION DE VARIABLES LOCALES
        nombre, dict_cta = tuple(cuenta)
        for key in dict_cta.keys():
                locals()[key] = dict_cta[key]
        
        ## CONFIRMACION DE CUENTA
        imprimir_cuenta(nombre, dict_cta)
        continuar = ingreso_bool('Continuar?')
        if not continuar:
            continue

        display_app_1 = """
        
        ============================================================
                    GENERADOR DE POSICIONES DE RIESGO
        ============================================================
"""
        print (display_app_1)

        ## SELECCION DEL PAR
        print ('Seleccione par a operar:')
        par = ingreso_bool_personalizado('BTC', 'XRP')
        print ('Obteniendo datos del contrato...')
        if not par:
            print ('Fallo la operativa')
            continue

        ##  1.2 Búsqueda de contrato
        # Actualizar a leer desde el archivo local
        from tools.api_bingx import cargar_contrato
        contrato = cargar_contrato(par)
        ##  1.3 Establecer datos de la cuenta
        #TODO: leer los datos desde un archivo externo
        cuenta = leer_cuenta('demo')      ##  ## TRADE: posición y entradas
        ##  1.5 Dirección del trade
        ##  1.6 Definición de la posición
        ##  1.7 Obtención del precio de referencia
        ##  1.8. Definición del tipo de orden
        ##  1.9 Definición de los targets


        ##  ## cálculo y registro operación
        ##  1.10 Cálculo del apalancamiento
        ##  1.11 Cálculo del lotaje por entrada
        ##  1.12 Confirmación de la operación
        ##  
        ##  ## ejecución del trade
        ##  1.13 Ejecución de la operación
        ##  1.14 Actualización del registro de la operación












    elif opcion == "2":
        from tools.ingresar_datos import activate_options, ingreso_bool_personalizado
        from tools.app_modules import productoria, calculo_operatoria

        display_app_conf = """
    ============================================================
                        CONFIGURACION DE LA APP
    ============================================================

    """
        print(display_app_conf)
        
        ### VERIFICACION DEL ESTADO DE LAS CUENTAS
        # VERIFICACION DE CUENTA ONLINE
        if not os.path.isfile('.env'):
            print('No se verifica la existencia del fichero .env que contanga API_KEY y SECRET_KEY\nChequear yt: https://youtu.be/AM0Yy-VUaIM\n')
        with open('cuentas/online.txt', 'r') as f:
            cuenta_online = f.read()
        if cuenta_online == '':
            print('No existe información de la cuenta online.\n')
        # VERIFICACION DE CUENTA OFFLINE
        with open('cuentas/offline.txt', 'r') as f:
            cuenta_offline = f.read()
        if cuenta_offline == '':
            print('No existe información de la cuenta offline.\n')


        opciones = ['Configuración cuenta', 'Seleccionar cuenta', 'Activar contrato para otros pares', 'Volver']        
        opcion_2 = activate_options(opciones)

        if opcion_2 == 'Configuración cuenta':
            print('\nSelecciona la cuenta que va a configurar:\n')
            nombre = ingreso_bool_personalizado('ONLINE', 'OFFLINE', 'OFFLINE')
            if not online and nombre == 'ONLINE':
                print('La cuenta online no está activa. Seleccione otra cuenta.')
                print ('Si ya creó el fichero .env, reinicie la app.\n')
                continue

            path = os.path.join(os.getcwd(), 'cuentas', nombre.lower() + '.txt')
            with open(path, 'r') as f:
                try:
                    dict_2_1 = eval(f.read())
                    print ('se verifican datos previos...\n')
                    for key, value in dict_2_1.items():
                        print ('{}: {}'.format(key, value))
                except:
                    print ('no se verifican datos previos')
                    dict_2_1 = {'vol_cta': 0, 'riesgo_op': 0.0, 'n_entradas': 0, 'vol_op': 0.0, 'vol_unidad': 0.0}

            opciones = ['Volumen Cuenta', 'Riesgo por operación', 'Cantidad de entradas por posición', 'Volver']
            while True:
                opcion_2_1 = activate_options(opciones)
                if not productoria(list(dict_2_1.values())) == 0:
                    if opcion_2_1 == 'Volver':
                        path = os.path.join(os.getcwd(), 'cuentas', nombre.lower() + '.txt')
                        with open(path, 'w') as f:
                            f.write(str(dict_2_1))
                        path = os.path.join(os.getcwd(), 'cuentas', 'active.pkl')
                        with open(path, 'wb') as f:
                            cuenta = nombre, dict_2_1
                            pickle.dump(cuenta, f)
                            imprimir_cuenta(nombre, dict_2_1)
                            print('\nPor favor, verifique que la información sea correcta\n')
                        break
                
                if opcion_2_1 == 'Volumen Cuenta':
                    if online:
                        dict_2_1['vol_cta'] = get_account_balance()
                        if dict_2_1['vol_cta'] == 0:
                            print ('La cuenta no posee fondos. Esto puede perjudicar el funcionamiento de la app.')
                            break
                    else:
                        dict_2_1['vol_cta'] = float(input('Ingrese el volumen de la cuenta: '))
                    dict_2_1['vol_op'], dict_2_1['vol_unidad'] = calculo_operatoria(dict_2_1)
                    print ()
                    continue
                elif opcion_2_1 == 'Riesgo por operación':
                    print('Ingrese el riesgo por operación:')
                    dict_2_1['riesgo_op'] = ingresar_tasa()
                    dict_2_1['vol_op'], dict_2_1['vol_unidad'] = calculo_operatoria(dict_2_1)
                    print ()
                    continue
                elif opcion_2_1 == 'Cantidad de entradas por posición':
                    dict_2_1['n_entradas'] = ingreso_entero('Ingrese la cantidad de entradas por posición: ')
                    dict_2_1['vol_op'], dict_2_1['vol_unidad'] = calculo_operatoria(dict_2_1)
                    print ()
                    continue
                elif opcion_2_1 == 'Volver':
                    if productoria(list(dict_2_1.values())) == 0:
                        print ('AUN FALTAN VARIABLES POR DEFINIR\n')

        elif opcion_2 == 'Seleccionar cuenta':
            print('\nSelecciona la cuenta que va a utilizar:\n')
            nombre = ingreso_bool_personalizado('ONLINE', 'OFFLINE', 'OFFLINE')
            if not online and nombre == 'ONLINE':
                print('La cuenta online no está activa. Seleccione otra cuenta.')
                print ('Si ya creó el fichero .env, reinicie la app.\n')
                continue

            path = os.path.join(os.getcwd(), 'cuentas', '{}.txt'.format(nombre.lower()))
            with open(path, 'r') as f:
                dict_2_1 = eval(f.read())
            path = os.path.join(os.getcwd(), 'cuentas', 'active.pkl')
            with open(path, 'wb') as f:
                pickle.dump([nombre, dict_2_1], f)
            print ('Cuenta {} activada'.format(nombre))

        elif opcion_2 == 'Activar contrato para otros pares':
            actualizar_contratos()
            print ('Próximas actualizaciones')
            pass

        elif opcion_2 == 'Volver':
            continue

        else:
            print("Opción inválida, por favor ingresa una opción válida.")


    elif opcion == "0":
        print("\nHasta luego!")
        break
    else:
        print("Opción inválida, por favor ingresa una opción válida.")
