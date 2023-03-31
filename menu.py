from tools.ingresar_datos import ingreso_bool, ingreso_bool_personalizado, entero_o_porcentual
from tools.api_bingx import cargar_contrato
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
for cuenta in CUENTAS:
    path = os.path.join(os.getcwd(), 'cuentas', cuenta)
    if not os.path.exists(path):
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
        # DEFINIR POSICION

        """
>>  PROCEDIMIENTO DE DEFINICIÓN DE OPERACIONES
        ## cuenta y operativa        
        1.1 Selección de par
        1.2 Búsqueda de contrato
        1.3 Establecer datos de la cuenta
        1.4 Confirmación de cuenta y operativa

        ## posición y entradas
        1.5 Dirección del trade
        1.6 Definición de la posición (Diversificación#TODO: si a una entrada se ingesa 0, el resto son 0)
        1.7 Obtención del precio de referencia
        1.8. Definición del tipo de orden
        1.9 Definición de los targets   #TODO: el valor porcentual del stoploss debe ser tomado en función de la entrada y no de la referencia
                                        #TODO: si el ingreso termina con un . se considera porcentual (ejemplo 3. == 3%, 3.5. == 3.5%)
        
        ## cálculo y registro operación
        1.10 Cálculo del apalancamiento
        1.11 Cálculo del lotaje por entrada
        1.12 Confirmación de la operación

        ## ejecución del trade
        1.13 Ejecución de la operación
        1.14 Actualización del registro de la operación
        """

        ##  ## cuenta y operativa        
        ##  1.1 Selección de par
        # Exactamente igual que como lo veniamos haciendo
        from tools.app_modules import seleccionar_par, leer_cuenta, leer_operativa, confirmar_cuenta
        par = seleccionar_par()
        ##  1.2 Búsqueda de contrato
        # Actualizar a leer desde el archivo local
        from tools.api_bingx import cargar_contrato
        contrato = cargar_contrato(par)
        ##  1.3 Establecer datos de la cuenta
        #TODO: leer los datos desde un archivo externo
        cuenta = leer_cuenta('demo')
        operativa = leer_operativa(cuenta)
        ##  1.4 Confirmación de cuenta y operativa
        #TODO: esto debe estar antes de definir la dirección del trade
        confirmar_cuenta(cuenta, operativa)

        ##  ## TRADE: posición y entradas
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
        from tools.ingresar_datos import create_options_display, activate_options

        # CONFIGURACION DE APP

        opciones = ['Configuración cuenta', 'Seleccionar cuenta', 'Activar contrato para otros pares', 'Volver']        

        display_app_conf = """
    ============================================================
                    CONFIGURACION DE LA APP
    ============================================================

    """
        print(display_app_conf)
        




        opcion_2 = activate_options(opciones)
        if opcion_2 == 'Configuración cuenta':
            opciones = ['Volumen Cuenta','Riesgo por operación','Cantidad de entradas por posición','Volver']
            pass

        elif opcion_2 == 'Seleccionar cuenta':
            pass

        elif opcion_2 == 'Activar contrato para otros pares':
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