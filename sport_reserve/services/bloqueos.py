from datetime import datetime

from ..constants import (
    ERROR_CODE_CANCHA_NOT_FOUND,
    ERROR_CODE_BLOQUEO_NOT_FOUND,
    ERROR_CODE_BLOQUEO_CONFLICT
)
from ..utils import construir_error_api
from ..validators.bloqueos import validar_body_bloqueo
from .. import db


def construir_bloqueo_dto(bloqueo: dict) -> dict:
    return {
        'id': bloqueo['id'],
        'id_cancha': bloqueo['id_cancha'],
        'fecha': str(bloqueo['fecha']),
        'hora_inicio': str(bloqueo['hora_inicio']),
        'hora_fin': str(bloqueo['hora_fin']),
        'motivo': bloqueo['motivo']
    }


def listar_bloqueos(params: dict) -> tuple[list[dict], int]:
    filas, total = db.obtener_bloqueos(
        id_cancha=params.get('id_cancha'),
        fecha=params.get('fecha'),
        limit=params['limit'],
        offset=params['offset']
    )

    return [construir_bloqueo_dto(b) for b in filas], total


def crear_bloqueo(body: dict) -> dict:
    datos = validar_body_bloqueo(body)

    cancha = db.obtener_cancha_por_id(datos['id_cancha'])

    if not cancha:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_CANCHA_NOT_FOUND,
            message='Cancha no encontrada',
            description=f"No existe una cancha con id '{datos['id_cancha']}'"
        ), 404)

    # Verificar superposición con reservas activas
    inicio = datetime.strptime(f"{datos['fecha']} {datos['hora_inicio']}", '%Y-%m-%d %H:%M:%S')
    fin = datetime.strptime(f"{datos['fecha']} {datos['hora_fin']}", '%Y-%m-%d %H:%M:%S')

    if db.existe_reserva_superpuesta(datos['id_cancha'], inicio, fin):
        raise ValueError(construir_error_api(
            code=ERROR_CODE_BLOQUEO_CONFLICT,
            message='La cancha tiene reservas en el intervalo',
            description='No se puede bloquear una cancha con reservas activas en el horario indicado'
        ), 409)

    if db.existe_bloqueo_superpuesto(datos['id_cancha'], datos['fecha'], datos['hora_inicio'], datos['hora_fin']):
        raise ValueError(construir_error_api(
            code=ERROR_CODE_BLOQUEO_CONFLICT,
            message='Existe un bloqueo superpuesto',
            description='Ya hay un bloqueo de mantenimiento en el mismo intervalo'
        ), 409)

    nuevo_id = db.insertar_bloqueo(
        datos['id_cancha'],
        datos['fecha'],
        datos['hora_inicio'],
        datos['hora_fin'],
        datos['motivo']
    )

    bloqueo = db.obtener_bloqueo_por_id(nuevo_id)

    return construir_bloqueo_dto(bloqueo)


def eliminar_bloqueo(id_bloqueo: int) -> None:
    eliminado = db.eliminar_bloqueo(id_bloqueo)

    if not eliminado:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_BLOQUEO_NOT_FOUND,
            message='Bloqueo no encontrado',
            description=f"No existe un bloqueo con id '{id_bloqueo}'"
        ), 404)
