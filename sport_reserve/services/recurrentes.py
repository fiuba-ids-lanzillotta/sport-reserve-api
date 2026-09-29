from datetime import datetime, timedelta

from ..constants import (
    ERROR_CODE_CANCHA_NOT_FOUND,
    ERROR_CODE_CANCHA_NOT_ACTIVE,
    ERROR_CODE_SOCIO_NOT_FOUND,
    ERROR_CODE_SOCIO_NOT_ACTIVE,
    ERROR_CODE_RESERVA_CONFLICT,
    MIN_CANTIDAD_SEMANAS,
    MAX_CANTIDAD_SEMANAS
)
from ..utils import (
    construir_error_api,
    parsear_fecha_hora,
    formatear_fecha_hora,
    validar_minimo,
    validar_maximo
)
from ..validators.recurrentes import validar_body_reserva_recurrente
from .. import db


def _calcular_precio_total(precio_hora: int, inicio: datetime, fin: datetime) -> int:
    horas = (fin - inicio).total_seconds() / 3600

    return int(precio_hora * horas)


def _verificar_disponibilidad(id_cancha: int, inicio: datetime, fin: datetime) -> bool:
    if db.existe_reserva_superpuesta(id_cancha, inicio, fin):
        return False

    if db.existe_bloqueo_superpuesto_para_reserva(id_cancha, inicio, fin):
        return False

    return True


def crear_reservas_recurrentes(body: dict) -> dict:
    datos = validar_body_reserva_recurrente(body)

    socio = db.obtener_socio_por_id(datos['id_socio'])

    if not socio:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_SOCIO_NOT_FOUND,
            message='Socio no encontrado',
            description=f"No existe un socio con id '{datos['id_socio']}'"
        ), 404)

    if not socio['activo']:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_SOCIO_NOT_ACTIVE,
            message='El socio no está activo',
            description='No se pueden crear reservas para un socio inactivo'
        ), 400)

    cancha = db.obtener_cancha_por_id(datos['id_cancha'])

    if not cancha:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_CANCHA_NOT_FOUND,
            message='Cancha no encontrada',
            description=f"No existe una cancha con id '{datos['id_cancha']}'"
        ), 404)

    if not cancha['activa']:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_CANCHA_NOT_ACTIVE,
            message='La cancha no está activa',
            description='No se pueden crear reservas en una cancha inactiva'
        ), 400)

    inicio_base = datos['fecha_hora_inicio']
    fin_base = datos['fecha_hora_fin']

    if fin_base <= inicio_base:
        raise ValueError(construir_error_api(
            code='invalid.fecha_hora_fin',
            message='El horario de fin debe ser posterior al de inicio',
            description="'fecha_hora_fin' debe ser mayor a 'fecha_hora_inicio'"
        ), 400)

    cantidad_semanas = datos['cantidad_semanas']
    validar_minimo(cantidad_semanas, MIN_CANTIDAD_SEMANAS, 'cantidad_semanas')
    validar_maximo(cantidad_semanas, MAX_CANTIDAD_SEMANAS, 'cantidad_semanas')

    precio_hora = cancha['precio_hora']
    reservas_a_crear = []
    conflictos = []

    for i in range(cantidad_semanas):
        inicio = inicio_base + timedelta(days=7 * i)
        fin = fin_base + timedelta(days=7 * i)

        if not _verificar_disponibilidad(datos['id_cancha'], inicio, fin):
            conflictos.append(inicio.date().isoformat())
            continue

        precio_total = _calcular_precio_total(precio_hora, inicio, fin)

        reservas_a_crear.append({
            'id_socio': datos['id_socio'],
            'id_cancha': datos['id_cancha'],
            'fecha_hora_inicio': inicio,
            'fecha_hora_fin': fin,
            'estado': 'confirmada',
            'precio_hora': precio_hora,
            'precio_total': precio_total
        })

    if conflictos:
        respuesta = construir_error_api(
            code=ERROR_CODE_RESERVA_CONFLICT,
            message='Algunas fechas de la serie no están disponibles',
            description='Las siguientes fechas presentan conflictos con reservas o bloqueos existentes'
        )
        respuesta['conflictos'] = conflictos
        raise ValueError(respuesta, 409)

    ids = db.insertar_reservas_batch(reservas_a_crear)

    reservas_creadas = []

    for id_reserva in ids:
        reserva = db.obtener_reserva_por_id(id_reserva)
        reservas_creadas.append({
            'id': reserva['id'],
            'id_socio': reserva['id_socio'],
            'id_cancha': reserva['id_cancha'],
            'fecha_hora_inicio': formatear_fecha_hora(reserva['fecha_hora_inicio']),
            'fecha_hora_fin': formatear_fecha_hora(reserva['fecha_hora_fin']),
            'estado': reserva['estado'],
            'precio_hora': reserva['precio_hora'],
            'precio_total': reserva['precio_total']
        })

    return {'reservas': reservas_creadas}
