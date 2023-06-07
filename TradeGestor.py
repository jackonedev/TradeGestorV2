import numpy as np
from tools.ingresar_datos import ingreso_bool_personalizado, ingresar_tasa, ingreso_entero, ingreso_bool, entero_o_porcentual, diversificar_entradas
from tools.api_bingx import actualizar_contratos, get_account_balance, get_price, get_benchmark, api_request
from tools.app_modules import comprobar_apis, imprimir_cuenta, cargar_contrato, apalancamiento, calcular_precio_liquidacion, generar_rows, obtener_sl, crear_directorio, alerta, verificar_fichero, definir_entradas
online = comprobar_apis()
import os
import pickle
from tools.api_bingx_v2 import switch_leverage, post_order
from datetime import datetime
from rich.console import Console
from rich.table import Table
import codecs
import locale
import csv, json
import time



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
    alerta(titulo='BIENVENDIO A TRADE GESTOR', mensaje='Por favor dirijase a la parte de configuración y configure su cuenta')
    print('\nBIENVENDIO A TRADE GESTOR\nPor favor dirijase a la parte de configuración y configure su cuenta')
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
        print ('\t(1) Seleccione par a operar:\n')
        par = ingreso_bool_personalizado('BTC', 'XRP')
        if not verificar_fichero(par):
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
        max_leverage_l = int(contract['maxLongLeverage'])
        max_leverage_s = int(contract['maxShortLeverage'])

        ##  1.3 Dirección del trade
        print ('\n\t(2) Indique dirección del trade:\n')
        direccion_trade = ingreso_bool_personalizado('LONG', 'SHORT')

        ## 1.4 Verificacion de la operativa
        export_data_inicial = """
>>    DATOS DE LA CUENTA {}
        - volumen cuenta  = {} USDT
        - riesgo por operación = {}%
        - volumen operacion = {} USDT

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
        print ('\n\t(3) Indique cuales ENTRADAS desea colocar:')
        estado_entradas = diversificar_entradas(n_entradas)
        if sum(estado_entradas) == 0:
            print ('No se ha seleccionado ninguna entrada')
            continue
        
        ##  1.6 Obtención del precio de referencia para los cálculos
        print ('\n\t(4) Obteniendo precio de {}\n'.format(symbol))
        benchmark = get_benchmark(symbol)
        if benchmark is None:
            continue


        ##  1.7 Diversificación de la posición (II)
        print ('\n\t(5) Definir targets de entrada:')
        target_entradas = definir_entradas(estado_entradas, benchmark, direccion_trade, currency, price_precision)

        # 1.8 Verificación de la congruencia de la operación
        for entrada, *_, sl in target_entradas:
            if direccion_trade == 'LONG':
                if entrada <= sl:
                    raise ValueError('En un trade LONG, la entrada no puede ser menor que el StopLoss')
            elif direccion_trade == 'SHORT':
                if entrada >= sl:
                    raise ValueError('En un trade SHORT, la entrada no puede ser mayor que el StopLoss')

        ##  1.9 Dimensionamiento del trade
        ordenes = [orden for _, orden, *_ in target_entradas]
        ##  1.9.1 Obteniendo entradas y sacando el promedio
        entradas = [entrada for entrada, *_ in target_entradas]
        entrada_promedio = np.mean(entradas)
        ## 1.9.3 Cantidad de activo en el contrato
        qty_entradas = [round(vol_unidad/abs(x[0] - x[-1]), qty_precision) for x in target_entradas]

        ## 1.9.4 Obtener el stop-loss más alejado
        sls = [sl for *_, sl in target_entradas]
        if direccion_trade == 'LONG':
            worst_sl = np.min(sls)
        elif direccion_trade == 'SHORT':
            worst_sl = np.max(sls)
        ## 1.9.3 Obtener el apalancamiento máximo
        apal_x, precio_liq = apalancamiento(entrada_promedio, worst_sl, direccion_trade)
        ## 1.9.4 Calcular el margen de la posición
        margen = round(entrada_promedio + sum(qty_entradas)/apal_x, 4)## calculado pero sin utilidad

        # 1.9.5 Verificación del estar dentro de los límites aceptables
        # 1.9.6 Verificación del precio de liquidacion
        if direccion_trade == 'LONG' and apal_x > max_leverage_l:
            print(f'El apalancamiento máximo para este par es de {max_leverage_l}x\nEl apalancamiento calculado es de {apal_x}x')
            print ('Desea apalancarse al máximo y utilizar un margen mayor de su cuenta?')
            continuar = ingreso_bool('Continuar?')
            if not continuar:
                continue
            else:
                apal_x = max_leverage_l
                precio_liq = calcular_precio_liquidacion(apal_x, entrada_promedio, direccion_trade)
                if precio_liq >= worst_sl:
                    print ('El precio de liquidación es superior al StopLoss')
                    print ('Falló la operativa')
                    continue
        if direccion_trade == 'SHORT' and apal_x > max_leverage_s:
            print(f'El apalancamiento máximo para este par es de {max_leverage_s}x\nEl apalancamiento calculado es de {apal_x}x')
            print ('Desea apalancarse al máximo y utilizar un margen mayor de su cuenta?')
            continuar = ingreso_bool('Continuar?')
            if not continuar:
                continue
            else:
                apal_x = max_leverage_s
                precio_liq = calcular_precio_liquidacion(apal_x, entrada_promedio, direccion_trade)
                if precio_liq <= worst_sl:
                    print ('El precio de liquidación es inferior al StopLoss')
                    print ('Falló la operativa')
                    continue



        ##  1.10... Descripción del trade
        export_data_trade =f"""
>>  DESCRIPCION TRADE {symbol} {direccion_trade}
        - Precio de referencia = {benchmark}
        - Entrada promedio = {round(entrada_promedio, price_precision)}
        - StopLoss más alejado = {round(worst_sl, price_precision)}
        - Apalancamiento = {apal_x}
        - Precio de liquidación = {round(precio_liq, price_precision)}
        - Total comerciado = {round(sum([round(qty_e, qty_precision) for qty_e in qty_entradas]), qty_precision)}
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


        # 1.9.1 Generar filas de la tabla
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
            i = 1
            file_name = f'{nombre}_{direccion_trade}_{par}_{fecha_actual.strftime("%d_{}").format(nombre_mes)}-01.txt'
        else:
            last_num = [int(x.split('-')[-1].split('.')[0]) for x in file_names]
            max_num = max(last_num)
            i = max_num + 1
            file_name = f'{nombre}_{direccion_trade}_{par}_{fecha_actual.strftime("%d_{}").format(nombre_mes)}-{i:02d}.txt'
        file_path = os.path.join(path, file_name)
        ## 1.11.4 Exportamos la data en formato .txt
        with codecs.open(file_path, 'w', encoding='utf-8') as f:
            f.write('TradeGestorDEMO: v2 \nCalculadora de riesgo y gestor de posiciones\nExchange: BingX\n')
            f.write(export_data_inicial)
            f.write(export_data_trade)
            f.write('\n\n\n')
            f.write(console.export_text())
            f.write(hora)
            # f.write('\n   -- Desarrollado por Jackone Action Software Company\n   -- jackone.action.software@gmail.com')
        print ('\n- Trade registrado bajo el nombre: {}'.format(file_name))

        ##  1.12 Exportar orden
        ## 1.12.1 Comprobar cuenta ONLINE
        if nombre == 'OFFLINE':
            print ('La cuenta OFFLINE no soporta colocación de órdenes.')
            print ('Volviendo al menu principal')
            continue
        path = os.path.join(os.getcwd(), 'ordenes')
        os.makedirs(path, exist_ok=True)
        file_names = os.listdir(path=path)
        file_name = f'{i:02d}_{direccion_trade}_{par}_{fecha_actual.strftime("%d_{}").format(nombre_mes)}.txt'
        file_path = os.path.join(path, file_name)
        with open(file_path, 'w') as f:
            f.write(direccion_trade)
            f.write('\n')
            f.write(str(contract))
            f.write('\n')
            f.write(str(target_entradas))
            f.write('\n')
            f.write(str(apal_x))
            f.write('\n')
            f.write(str(qty_entradas))
        print('- Orden exportada en: {}\n'.format(file_name))
        

        ## 1.13 COLOCACION DE ORDENES
        colocar_ordenes = ingreso_bool('\nDesea colocar las ordenes?')
        if not colocar_ordenes:
            print('Volviendo al menu principal')
            continue


        spread = 0.00035
        symbol = symbol
        positionSide = direccion_trade
        # apalancamiento = apal_x
        monto_entrada = qty_entradas

        if positionSide == 'LONG':
            entrada_side = 'BUY'
            sl_side = 'SELL'
        elif positionSide == 'SHORT':
            entrada_side = 'SELL'
            sl_side = 'BUY'


        print('''
        ============================================================
                            GENERANDO ORDENES
        ============================================================
        ''')
        ordenes = []
        for i in range(len(target_entradas)):
            entrada = {}
            sl = {}

            type_entrada = target_entradas[i][1]
            type_sl = 'TRIGGER_MARKET'#STOP_MARKET: promedia los stoploss

            if type_entrada=='TRIGGER_MARKET':
                benchmark = get_price(symbol)
                if positionSide == 'LONG':
                    stopPrice = benchmark * (1 - spread)
                elif positionSide == 'SHORT':
                    stopPrice = benchmark * (1 + spread)

            quantity = monto_entrada[i]
            
            orden = {
                "symbol": symbol,
                "positionSide": positionSide,
                'quantity': quantity
            }

            entrada.update(orden)
            entrada.update({'side': entrada_side,'type': type_entrada})
            sl.update(orden)
            sl.update({'side': sl_side,'type': type_sl})
            if type_entrada == 'TRIGGER_MARKET':
                dif_sl = benchmark * target_entradas[i][2] /100
                if positionSide == 'LONG':
                    sl_price = benchmark - dif_sl
                else:
                    sl_price = benchmark + dif_sl
                sl.update({'stopPrice': sl_price})
            else:
                sl.update({'stopPrice': target_entradas[i][-1]})
            ##
            if type_entrada.find('LIMIT') != -1:
                entrada.update({'price': target_entradas[i][0]})
            elif type_entrada.find('TRIGGER') != -1:
                entrada.update({'stopPrice':stopPrice})

            ordenes.append((entrada, sl))



        for i in range(len(target_entradas)):
            print(f'''
            ORDEN DE ENTRADA {i+1}
            ''')
            print(ordenes[i][0])
            print(f'''
            ORDEN DE STOP LOSS {i+1}
            ''')
            print(ordenes[i][1])


        print('''
        ============================================================
                            COLOCANDO ORDENES
        ============================================================
        ''')
        print('\n\t(6) Verificando apalancamiento\n')
        # COMPROBAR ESTADO DE LAS ORDENES EN EL EXCHANGE
        ## AJUSTAR EL APALANCAMIENTO EN CASO QUE SEA NECESARIO
        ## TODO: la función api_requests del modulo tools.api_bingx está en desuso y debe ser reemplazada por el módulo v2
        response = api_request(service='/openApi/swap/v2/trade/openOrders', header=True, sign=True)
        ordenes_exchange = response['data']['orders']
        existe_orden = False
        if len(ordenes_exchange) > 0:# si existen ordenes abiertas
            for ord in ordenes_exchange:
            # verificar que las ordenes sean del symbol correcto
                if ord['symbol'] == symbol:
                    existe_orden = True
                    break






        if existe_orden:

            # consultar apalancamiento
            response = api_request(service='/openApi/swap/v2/trade/leverage', query_params=f"symbol={symbol}" ,header=True, sign=True)
            apal_ord = response['data']
            # verificar dirección del trade y tamaño del apalancamiento
            for apal_side in apal_ord.keys():
                if apal_side.find(positionSide.lower()) != -1:
                    apal_size = apal_ord[apal_side]
            # comprobar que el apalancamiento de las ordenes sea el mismo que el que se quiere colocar
            if apal_size != apal_x:
                print('Existen ordenes en ese par con un apalancamiento diferente')
                exit()
            
            ## comentario: si existen ordenes y el apalancamiento es el mismo no hace falta actualizar.




            # if not existe_orden:
            #     response = switch_leverage(symbol, direccion_trade, apal_x)
            #     if response['code'] == 0:
            #         print ('Actualización de apalancamiento OK: {}'.format(response['data']))
            #     else:
            #         print ('Error al actualizar el apalancamiento: {}'.format(response['msg']))
            #         exit()
        # Si no existen ordenes previas, configurar apalancamiento
        else:
            response = switch_leverage(symbol, direccion_trade, apal_x)
            if response['code'] == 0:
                print ('Actualización de apalancamiento OK: {}'.format(response['data']))
            else:
                print ('Error al actualizar el apalancamiento: {}'.format(response['msg']))
                exit()


        print('\n\t(7) Enviando ordenes\n')
        print('Colocando ordenes...')

        #
        # COLOCACION DE LAS ORDENES
        #
        responses = []
        for i in range(len(target_entradas)):
            response_entrada = post_order(**ordenes[i][0])
            if response_entrada['code'] == 0:
                print ('Orden de entrada OK: {}'.format(response['data']))
            else:
                print ('Error al colocar la orden de entrada: {}'.format(response['msg']))
                exit()
            response_sl = post_order(**ordenes[i][1])
            if response['code'] == 0:
                print ('Orden de stop loss OK: {}'.format(response['data']))
            else:
                print ('Error al colocar la orden de stop loss: {}'.format(response['msg']))
                exit()
            responses.append((response_entrada, response_sl))


        # export responses as json
        with open('responses.json', 'a') as f:
            f.write(json.dumps(responses) + '\n')


        # Verificar si el archivo ya existe
        headers_exist = True
        if not os.path.exists('responses.csv'):
            headers_exist = False

        # export responses as csv
        with open('responses.csv', 'a', newline='') as f:
            writer = csv.writer(f)

            # Escribir los encabezados de las columnas en el archivo
            if not headers_exist:
                writer.writerow(['symbol', 'orderId', 'side', 'positionSide', 'type'])

            # Escribir cada registro en el archivo
            for respuesta in responses:
                for sub_respuesta in respuesta:
                    order = sub_respuesta['data']['order']
                    writer.writerow([order['symbol'], order['orderId'], order['side'], order['positionSide'], order['type']])


        print('''\n\nFinalización de la ejecución del trade, no sé olvide de gestionar su TakeProfit y ordenes abiertas. Muchas gracias por usar la calculadora''')


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
