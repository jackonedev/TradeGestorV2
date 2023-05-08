import datetime
import pandas as pd


def past_timestamp(cantidad, periodo):
    "Devuelve en milisegundos el timestamp de hace 'cantidad' 'periodo'"
    if periodo == "min":
        delta = datetime.timedelta(minutes=cantidad)
    elif periodo == "hour":
        delta = datetime.timedelta(hours=cantidad)
    elif periodo == "days":
        delta = datetime.timedelta(days=cantidad)
    else:
        raise ValueError("Período inválido")
    
    now = datetime.datetime.now()
    past = now - delta
    timestamp = datetime.datetime.timestamp(past)
    return timestamp * 1000


def now_timestamp():
    "devuelve en milisegundos el timestamp actual"
    return datetime.datetime.timestamp(datetime.datetime.now()) * 1000


def retrasar_tres_horas(fecha_hora):
    """Comprueba si la fecha y hora están completas y les resta tres horas"""
    # Comprobar si es una cadena de texto
    if isinstance(fecha_hora, str):
        if fecha_hora.find(':') == -1:
            # No es una fecha y hora completa, no se aplica el retraso
            return fecha_hora
    fecha_hora_retrasada = pd.to_datetime(fecha_hora) - datetime.timedelta(hours=3)
    return fecha_hora_retrasada.strftime('%Y-%m-%d %H:%M:%S')

