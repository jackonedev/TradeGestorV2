import os
import pandas as pd

def guardar_csv(path_output, data):
    """
    Guarda un DataFrame como archivo CSV en la ruta especificada.

    Argumentos:
    - path_output: ruta relativa o absoluta donde se guardará el archivo CSV.
    - data: DataFrame a guardar como archivo CSV.

    """
    # Obtener el path absoluto del archivo de salida
    path_absoluto_output = os.path.abspath(path_output)
    print('Guardando en ubicación:')
    print(path_absoluto_output)
    # Abrir el archivo de salida
    with open(path_absoluto_output, 'w') as archivo_output:
        # Guardar el archivo csv
        data.to_csv(archivo_output, index=False)

def crear_directorio(path_output):
    """
    Crea un directorio en la ruta especificada si este no existe. Si el directorio ya existe, se muestra un mensaje indicando
    la ubicación del directorio existente.

    Argumentos:
    - path_output: ruta relativa o absoluta donde se creará el directorio.

    """
    path_absoluto_output = os.path.abspath(path_output)
    if not os.path.exists(path_absoluto_output):
        os.makedirs(path_absoluto_output)

def leer_csv(path_input: str) -> pd.DataFrame:
    """
    Lee un archivo CSV en la ruta especificada y lo retorna como un objeto DataFrame de Pandas.

    Argumentos:
    - path_input: ruta relativa o absoluta donde se encuentra el archivo CSV.

    Retorna:
    - data: DataFrame de Pandas con los datos del archivo CSV.

    """
    # Obtener el path absoluto del archivo de entrada
    path_absoluto_input = os.path.abspath(path_input)
    print('Leyendo ubicación:')
    print(path_absoluto_input)
    # Abrir el archivo de entrada
    data = None
    with open(path_absoluto_input, 'r') as archivo_input:
        # Leer el archivo csv
        data = pd.read_csv(archivo_input)
    # Retornar la data
    if not isinstance(data, type(None)):
        return data