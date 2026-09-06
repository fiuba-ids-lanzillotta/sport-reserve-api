from datetime import datetime, timedelta

from ..constants import (
    ERROR_CODE_CANCHA_NOT_FOUND,
    ERROR_CODE_CANCHA_NOT_ACTIVE,
    ERROR_CODE_SOCIO_NOT_FOUND,
    ERROR_CODE_SOCIO_NOT_ACTIVE,
    ERROR_CODE_RESERVA_NOT_FOUND,
    ERROR_CODE_RESERVA_CONFLICT,
    ERROR_CODE_RESERVA_ESTADO_INVALIDO,
    ERROR_CODE_RESERVA_ESTADO_TRANSICION,
    ERROR_CODE_RESERVA_ESTADO_TEMPORAL
)
from ..utils import (
    construir_error_api,
    parsear_fecha_hora,
    formatear_fecha_hora
)
from ..validators.reservas import (
    validar_body_reserva,
    validar_body_estado_reserva
)
from .. import db


def construir_reserva_dto(reserva: dict) -> dict:
    return {
        'id': reserva['id'],
        'id_socio': reserva['id_socio'],
        'id_cancha': reserva['id_cancha'],
        'fecha_hora_inicio': formatear_fecha_hora(reserva['fecha_hora_inicio']),
        'fecha_hora_fin': formatear_fecha_hora(reserva['fecha_hora_fin']),
        'estado': reserva['estado'],
        'precio_hora': reserva['precio_hora'],
        'precio_total': reserva['precio_total']
    }


def _calcular_precio_total(precio_hora: int, inicio: datetime, fin: datetime) -> int:
    horas = (fin - inicio).total_seconds() / 3600
    return int(precio_hora * horas)


def _verificar_disponibilidad(id_cancha: int, inicio: datetime, fin: datetime, excluir_reserva_id=None) -> None:
    if db.existe_reserva_superpuesta(id_cancha, inicio, fin, excluir_reserva_id):
        raise ValueError(construir_error_api(
            code=ERROR_CODE_RESERVA_CONFLICT,
            message='La cancha no está disponible en el horario solicitado',
            description='El intervalo se superpone con una reserva existente'
        ), 409)


def listar_reservas(params: dict) -> tuple[list[dict], int]:
    filas, total = db.obtener_todas_las_reservas(
        id_cancha=params.get('id_cancha'),
        id_socio=params.get('id_socio'),
        estado=params.get('estado'),
        fecha_desde=params.get('fecha_desde'),
        fecha_hasta=params.get('fecha_hasta'),
        limit=params['limit'],
        offset=params['offset']
    )

    return [construir_reserva_dto(r) for r in filas], total


def crear_reserva(body: dict) -> dict:
    datos = validar_body_reserva(body)

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

    inicio = datos['fecha_hora_inicio']
    fin = datos['fecha_hora_fin']

    if fin <= inicio:
        raise ValueError(construir_error_api(
            code='invalid.fecha_hora_fin',
            message='El horario de fin debe ser posterior al de inicio',
            description="'fecha_hora_fin' debe ser mayor a 'fecha_hora_inicio'"
        ), 400)

    _verificar_disponibilidad(datos['id_cancha'], inicio, fin)

    precio_hora = cancha['precio_hora']
    precio_total = _calcular_precio_total(precio_hora, inicio, fin)

    nuevo_id = db.insertar_reserva(
        datos['id_socio'],
        datos['id_cancha'],
        inicio,
        fin,
        'confirmada',
        precio_hora,
        precio_total
    )

    reserva = db.obtener_reserva_por_id(nuevo_id)
    return construir_reserva_dto(reserva)


def buscar_reserva_por_id(id_reserva: int) -> dict:
    reserva = db.obtener_reserva_por_id(id_reserva)

    if not reserva:
        return {}

    return construir_reserva_dto(reserva)


def cambiar_estado_reserva(id_reserva: int, body: dict) -> dict:
    reserva = db.obtener_reserva_por_id(id_reserva)

    if not reserva:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_RESERVA_NOT_FOUND,
            message='Reserva no encontrada',
            description=f"No existe una reserva con id '{id_reserva}'"
        ), 404)

    datos = validar_body_estado_reserva(body)
    nuevo_estado = datos['estado']
    estado_actual = reserva['estado']

    if nuevo_estado == estado_actual:
        return construir_reserva_dto(reserva)

    inicio = reserva['fecha_hora_inicio']
    fin = reserva['fecha_hora_fin']
    ahora = datetime.now()

    # Validar transiciones de estado y restricciones temporales
    if estado_actual == 'confirmada':
        if nuevo_estado == 'cancelada':
            if ahora >= inicio:
                raise ValueError(construir_error_api(
                    code=ERROR_CODE_RESERVA_ESTADO_TEMPORAL,
                    message='No se puede cancelar la reserva',
                    description='No se puede cancelar una reserva que ya comenzó o finalizó'
                ), 400)
        elif nuevo_estado == 'finalizada':
            if ahora < fin:
                raise ValueError(construir_error_api(
                    code=ERROR_CODE_RESERVA_ESTADO_TEMPORAL,
                    message='No se puede finalizar la reserva',
                    description='No se puede finalizar una reserva antes de su horario de fin'
                ), 400)
        else:
            raise ValueError(construir_error_api(
                code=ERROR_CODE_RESERVA_ESTADO_TRANSICION,
                message='Transición de estado inválida',
                description=f"No se puede pasar de '{estado_actual}' a '{nuevo_estado}'"
            ), 400)

    elif estado_actual == 'cancelada':
        if nuevo_estado == 'confirmada':
            if ahora >= inicio:
                raise ValueError(construir_error_api(
                    code=ERROR_CODE_RESERVA_ESTADO_TEMPORAL,
                    message='No se puede reactivar la reserva',
                    description='No se puede reactivar una reserva cuyo horario ya comenzó o finalizó'
                ), 400)

            _verificar_disponibilidad(reserva['id_cancha'], inicio, fin, excluir_reserva_id=id_reserva)
        else:
            raise ValueError(construir_error_api(
                code=ERROR_CODE_RESERVA_ESTADO_TRANSICION,
                message='Transición de estado inválida',
                description=f"No se puede pasar de '{estado_actual}' a '{nuevo_estado}'"
            ), 400)

    elif estado_actual == 'finalizada':
        raise ValueError(construir_error_api(
            code=ERROR_CODE_RESERVA_ESTADO_TRANSICION,
            message='Transición de estado inválida',
            description='Una reserva finalizada no puede cambiar de estado'
        ), 400)

    db.actualizar_estado_reserva(id_reserva, nuevo_estado)
    reserva = db.obtener_reserva_por_id(id_reserva)
    return construir_reserva_dto(reserva)
