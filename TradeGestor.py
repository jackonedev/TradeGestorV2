import numpy as np
from tools.ingresar_datos import ingreso_bool_personalizado, ingresar_tasa, ingreso_entero, ingreso_bool, entero_o_porcentual
from tools.api_bingx import actualizar_contratos, get_account_balance, get_price
from tools.app_modules import comprobar_apis, imprimir_cuenta, cargar_contrato, apalancamiento, generar_rows, obtener_sl, crear_directorio
online = comprobar_apis()
import os
import pickle
from itertools import count
from datetime import datetime
from rich.console import Console
from rich.table import Table
import codecs
import locale

locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")

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



#############################################################################################################
#############################################################################################################
#############################################################################################################
#############################################################################################################
#                                       CALCULADORA DE POSICIONES                                           #
#############################################################################################################
#############################################################################################################
#############################################################################################################
#############################################################################################################


    if opcion == "1":
        ## MAIN APP

        ## LECTURA DE LA CUENTA
        path = os.path.join(os.getcwd(), 'cuentas', 'active.pkl')
        with open(path, 'rb') as f:
            cuenta = pickle.load(f)
            if not isinstance(cuenta, list) and len(cuenta)==2:
                print('La cuenta activa no tiene el formato correcto')
                continue
            elif cuenta == '--.. .- .-. - . -..- .--. .-. ---':
                print('Bienvenido a TradeGestorDEMO\nPor favor dirijase a la parte de configuración de cuenta')
                continue

        ##  DESEMPAQUE Y CREACION DE VARIABLES LOCALES
        nombre, dict_cta = tuple(cuenta)
        for key in dict_cta.keys():
                locals()[key] = dict_cta[key]

        if nombre == 'ONLINE':
            try:
                vol_cta = get_account_balance()
            except:
                print ('Ocurrió un error al querer actualizar el volumen de la cuenta')

        ## CONFIRMACION DE CUENTA
        imprimir_cuenta(nombre, dict_cta)
        continuar = ingreso_bool('\nContinuar?')
        if not continuar:
            continue

        display_app_1 = """
        
        ============================================================
                    GENERADOR DE POSICIONES DE RIESGO
        ============================================================
"""
        print (display_app_1)

        ## 1.1 Selección del par a operar
        print ('Seleccione par a operar:')
        par = ingreso_bool_personalizado('BTC', 'XRP')
        path = os.path.join(os.getcwd(), 'contratos')
        if not os.path.exists(path):
            print ('Por favor vaya a configuración y seleccione Descargar contratos')
            print ('Falló la operativa')
            continue

        ##  1.2 Búsqueda de contrato, y obtención de cifras significativas
        contract = cargar_contrato(par)
        if not contract:
            print ('No se encontró el contrato')
            print ('Falló la operativa')
            continue
        par = contract['asset']
        currency = contract['currency']
        symbol = contract['symbol']
        qty_precision = contract['quantityPrecision']
        price_precision = contract['pricePrecision']
        max_leverage_l = contract['maxLongLeverage']
        max_leverage_s = contract['maxShortLeverage']


        ##  1.3 Dirección del trade
        print ('Indique dirección del trade:')
        direccion_trade = ingreso_bool_personalizado('LONG', 'SHORT')

        ## 1.4 Verificacion de la operativa
        export_data_inicial = """
>>    DATOS DE LA CUENTA {}
        - volumen cuenta  = {}
        - riesgo por operación = {}%
        - volumen operacion = {}

>>    DATOS DE LA OPERACION EN {}
        - par = {}
        - nº entradas = {}
        - volumen por entrada = {} {}
        """.format(nombre, vol_cta, riesgo_op, vol_op, direccion_trade, symbol, n_entradas, round(vol_unidad,2), currency)
        print (export_data_inicial)


        continuar = ingreso_bool('Continuar?')
        if not continuar:
            continue


        ## 1.5 Diversificación de la posición (I)
        print ('Indique cuales ENTRADAS desea colocar:')
        estado_entradas = []
        for i in range(n_entradas):
            estado_entradas.append(ingreso_bool(f'Colocar ENTRADA Nº {i+1}?'))
        print (f'Entradas COLOCADAS: {sum(estado_entradas)}  |  Entradas ANULADAS: {len(estado_entradas)-sum(estado_entradas)}')
        
        
        ##  1.6 Obtención del precio de referencia para los cálculos
        print ('Obteniendo precio de {}...'.format(symbol))
        try:
            benchmark = get_price(symbol)
        except:
            print ('Error al obtener precio...\nPor favor ingreselo manualmente')
            benchmark = float(input('Precio de {} = '.format(par)))
        print ('Precio actual de {} = {} {}'.format(symbol, benchmark, currency))

        ##  1.7 Diversificación de la posición (II)
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
                        entrada = benchmark
                else:
                    print ('Falló la operativa')
                    continue
                #TODO: revisar print# print ('Orden {} en el nivel = {} {}'.format(tipo_orden, entrada, currency))
                # 1.7.3 Precio de stoploss
                sl, pct = entero_o_porcentual('Indique precio de STOPLOSS:')
                chance_sl = count(1)
                sl = obtener_sl(entrada, sl, pct, direccion_trade)
                if not sl:
                    print('error en la operativa- el stop loss quedó vacio')
                    while next(chance_sl) < 5:
                        sl, pct = entero_o_porcentual('Indique precio de STOPLOSS:')
                        sl = obtener_sl(entrada, sl, pct, direccion_trade)
                        if not sl:
                            print('error en la operativa- el stop loss quedó vacio')
                #TODO: revisar print# print ('StopLoss = {} {}'.format(sl, currency))
                target_entradas.append((entrada, tipo_orden, sl))

                # 1.7.4 Verificación de la congruencia de la operación
                for entrada, _, sl in target_entradas:
                    if direccion_trade == 'LONG':
                        if entrada <= sl:
                            raise ValueError('En un trade LONG, la entrada no puede ser menor que el StopLoss')
                    elif direccion_trade == 'SHORT':
                        if entrada >= sl:
                            raise ValueError('En un trade SHORT, la entrada no puede ser mayor que el StopLoss')


        ##  1.8 Dimensionamiento del trade
        ordenes = [orden for _, orden, _ in target_entradas]
        ##  1.8.1 Obteniendo entradas y sacando el promedio
        entradas = [entrada for entrada, *_ in target_entradas]
        entrada_promedio = np.mean(entradas)
        ## 1.8.2 Obtener el stop-loss más alejado
        sls = [sl for *_, sl in target_entradas]
        if direccion_trade == 'LONG':
            worst_sl = np.min(sls)
        elif direccion_trade == 'SHORT':
            worst_sl = np.max(sls)
        ## 1.8.3 Obtener el apalancamiento máximo
        apal_x, precio_liq = apalancamiento(entrada_promedio, worst_sl, direccion_trade)



        ###TODO: APALANCAMIENTO -> SI ES MAYOR AL MAXIMO ADMITIDO CONFIGURAR UNA NUEVA ALTERNATIVA DE RESOLUCION
        if direccion_trade == 'LONG' and apal_x > max_leverage_l:
            print(f'El apalancamiento máximo para este par es de {max_leverage_l}x\nEl apalancamiento calculado es de {apal_x}x')
            print ('Desea apalancarse al máximo y utilizar un margen mayor de su cuenta?')
            continuar = ingreso_bool('Continuar?')
            if not continuar:
                continue
            else:
                apal_x = max_leverage_l
        if direccion_trade == 'SHORT' and apal_x > max_leverage_s:
            print(f'El apalancamiento máximo para este par es de {max_leverage_s}x\nEl apalancamiento calculado es de {apal_x}x')
            print ('Desea apalancarse al máximo y utilizar un margen mayor de su cuenta?')
            continuar = ingreso_bool('Continuar?')
            if not continuar:
                continue
            else:
                apal_x = max_leverage_s
                
        ## 1.8.4 Obtener la cantidad de monedas a adquirir por entrada
        qty_entradas = [round(vol_unidad/abs(x[0] - x[-1]),qty_precision) for x in target_entradas]


        ##  1.9 Descripción del trade
        export_data_trade =f"""
>>  DESCRIPCION TRADE {symbol} {direccion_trade}
        - Precio de referencia = {benchmark}
        - Entrada promedio = {round(entrada_promedio, price_precision)}
        - StopLoss más alejado = {round(worst_sl, price_precision)}
        - Apalancamiento = {apal_x}
        - Precio de liquidación = {round(precio_liq, price_precision)}
        - Total comerciado = {sum([round(qty_e, qty_precision) for qty_e in qty_entradas])}
        - Pérdidas peor escenario = {round(sum([abs(entradas[i] - sls[i])*qty_entradas[i] for i in range(sum(estado_entradas))]), 2)}
        """
        print (export_data_trade)

        console = Console(record=True)
        table = Table(title="RESUMEN ENTRADAS: {} | PAR: {}".format(direccion_trade, par))
    
        table.add_column("Nº", justify="right", style="cyan", no_wrap=True)
        table.add_column("CONDICION", style="cyan")
        table.add_column("ORDEN", style="cyan")
        table.add_column("ENTRADA", justify="right", style="cyan")
        table.add_column("STOPLOSS", justify="right", style="cyan")
        table.add_column("CANTIDAD", justify="right", style="cyan")
        table.add_column("RIESGO", justify="right", style="cyan")


        #TODO: actualizar RIESGO
        id_1, estado_2, orden_3, entrada_4, sl_5, cantidad_6, riesgo_7 = generar_rows(n_entradas, estado_entradas,ordenes, entradas, sls, qty_entradas, price_precision, qty_precision)
        for i in range(n_entradas):
            table.add_row(id_1[i], estado_2[i], orden_3[i], entrada_4[i], sl_5[i], cantidad_6[i], riesgo_7[i])
        console.print(table)

        ##  1.10 Confirmar trade
        continuar = ingreso_bool('\nDesea confirmar el trade?')
        if not continuar:
            continue
        
        ##  1.11 Exportar datos
        ##  1.11.1 Creamos el directorio "registro"
        path = os.path.join(os.getcwd(), 'registro')
        os.makedirs(path, exist_ok=True)

        ##  1.11.2 Obtenemos datos del fecha y hora actual
        fecha_actual = datetime.now()
        nombre_mes = fecha_actual.strftime("%B")
        hora = '\n\n\nTrade calculado el día {} a las {}'.format(fecha_actual.strftime("%d de {mes} de %Y").format(mes=nombre_mes.title()), fecha_actual.strftime("%H:%M:%S"))

        ## 1.11.3 Verificamos los nombre existentes y definimos nombre
        file_names = os.listdir(path=path)
        if len(file_names) == 0:
            file_name = f'{nombre}_{direccion_trade}_{par}_{fecha_actual.strftime("%d_{}").format(nombre_mes)}-01.txt'
        else:
            last_file = file_names[-1]
            i = last_file.split('-')[-1]
            i = int(i.split('.')[0])
            file_name = f'{nombre}_{direccion_trade}_{par}_{fecha_actual.strftime("%d_{}").format(nombre_mes)}-{i+1:02d}.txt'
        file_name = os.path.join(path, file_name)
        ## 1.11.4 Exportamos la data en formato .txt
        with codecs.open(file_name, 'w', encoding='utf-8') as f:
            f.write('TradeGestorDEMO: v2 \nCalculadora de riesgo y gestor de posiciones\nExchange: BingX\n')
            f.write(export_data_inicial)
            f.write(export_data_trade)
            f.write('\n\n\n')
            f.write(console.export_text())
            f.write(hora)
            # f.write('\n   -- Desarrollado por Jackone Action Software Company\n   -- jackone.action.software@gmail.com')

        print ('Trade registrado bajo el nombre: {}'.format(file_name))

        ##  1.12 Ejecutar orden
        ## 1.12.1 Comprobar cuenta ONLINE
        if nombre == 'OFFLINE':
            print ('La cuenta OFFLINE no soporta colocación de órdenes.')
            print ('Volviendo al menu principal')
            continue
        print ('Todavía en desarrollo, muchas gracias por utilizar TradeGestorDEMO versión ONLINE')

#############################################################################################################
#############################################################################################################
#############################################################################################################
#############################################################################################################
#                                       CONFIGURACION DE LA APP                                             #
#############################################################################################################
#############################################################################################################
#############################################################################################################
#############################################################################################################





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


        opciones = ['Configuración cuenta', 'Seleccionar cuenta', 'Descarga de contratos', 'Volver']        
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
                        print ()
                except:
                    print ('no se verifican datos previos\n')
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
                            cuenta = [nombre, dict_2_1]
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
                try:
                    dict_2_1 = eval(f.read())
                except:
                    print ('No se encontró información de la cuenta {}\n'.format(nombre))
                    continue
            path = os.path.join(os.getcwd(), 'cuentas', 'active.pkl')
            with open(path, 'wb') as f:
                pickle.dump([nombre, dict_2_1], f)
            print ('Cuenta {} activada'.format(nombre))

        elif opcion_2 == 'Descarga de contratos':
            crear_directorio('contratos')
            actualizar_contratos()
            print ('Contratos actualizados\n')

        elif opcion_2 == 'Volver':
            continue

        else:
            print("Opción inválida, por favor ingresa una opción válida.")


    elif opcion == "0":
        print("\nHasta luego!")
        break
    else:
        print("Opción inválida, por favor ingresa una opción válida.")
