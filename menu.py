from tools.ingresar_datos import ingreso_bool, ingreso_bool_personalizado, entero_o_porcentual
from tools.api_bingx import cargar_contrato

print ('''
    ============================================================
            BIENVENIDO A LA MEJOR CALCULADORA DE RIESGO
    ============================================================
TradeGestorDEMO v2
Exchange: BingX
Cuenta: Future Perpetual
    ''')







while True:
    menu = """
>>  MENU PRINCIPAL
    
    1. Definir posición
    2. Seguimiento posición
    3. Configuración
    0. Salir
"""
    print(menu)

    opcion = input("Ingrese una opción: ")

    if opcion == "1":
        # SETEO DE LAS VARIABLES INICIALES
        print ('Seleccione par a operar:')
        par = ingreso_bool_personalizado('BTC', 'XRP', 'user-input')
        try:
            print ('Obteniendo datos del contrato...')
            contract = cargar_contrato(par)
        except:
            print ('Búsqueda de contrato fallida')
        continue

        qty_precision = contract['quantityPrecision']
        price_precision = contract['pricePrecision']

        ## ESTABLECER EL APALANCAMIENTO MAXIMO DEL PAR (OBTENIDO MANUALMENTE INGRESANDO A LA PLATFORMA)#TODO: exportar esta data a un archivo externo
        if par == 'BTC':
            apalancamiento_maximo = 150
        elif par == 'XRP':
            apalancamiento_maximo = 125
        # Aquí puedes agregar el código que deseas ejecutar para la opción 1
        print()
        print (contract)











    elif opcion == "2":
        print("Has elegido la opción 2")
        # Aquí puedes agregar el código que deseas ejecutar para la opción 2
    elif opcion == "0":
        print("Hasta luego!")
        break # Termina el ciclo while y sale del programa
    else:
        print("Opción inválida, por favor ingresa una opción válida.")