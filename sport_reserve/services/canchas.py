from ..constants import (
    ERROR_CODE_DEPORTE_NOT_FOUND,
    ERROR_CODE_CANCHA_NOT_FOUND,
    ERROR_CODE_CANCHA_HAS_RESERVAS
)
from ..utils import construir_error_api
from ..validators.canchas import (
    validar_body_cancha,
    validar_body_cancha_patch
)
from .. import db


def construir_cancha_dto(cancha: dict) -> dict:
    return {
        'id': cancha['id'],
        'nombre': cancha['nombre'],
        'id_deporte': cancha['id_deporte'],
        'precio_hora': cancha['precio_hora'],
        'techada': bool(cancha['techada']),
        'activa': bool(cancha['activa'])
    }


def listar_canchas(params: dict) -> tuple[list[dict], int]:
    filas, total = db.obtener_canchas(
        id_deporte=params.get('id_deporte'),
        nombre=params.get('nombre'),
        techada=params.get('techada'),
        activa=params.get('activa'),
        limit=params['limit'],
        offset=params['offset']
    )

    return [construir_cancha_dto(c) for c in filas], total


def crear_cancha(body: dict) -> dict:
    datos = validar_body_cancha(body)

    deporte = db.obtener_deporte_por_id(datos['id_deporte'])

    if not deporte:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_DEPORTE_NOT_FOUND,
            message='Deporte no encontrado',
            description=f"No existe un deporte con id '{datos['id_deporte']}'"
        ), 404)

    nuevo_id = db.insertar_cancha(
        datos['nombre'],
        datos['id_deporte'],
        datos['precio_hora'],
        datos['techada'],
        datos['activa']
    )

    cancha = db.obtener_cancha_por_id(nuevo_id)

    return construir_cancha_dto(cancha)


def buscar_cancha_por_id(id_cancha: int) -> dict:
    cancha = db.obtener_cancha_por_id(id_cancha)

    if not cancha:
        return {}

    return construir_cancha_dto(cancha)


def actualizar_cancha_parcial(id_cancha: int, body: dict) -> dict:
    cancha = db.obtener_cancha_por_id(id_cancha)

    if not cancha:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_CANCHA_NOT_FOUND,
            message='Cancha no encontrada',
            description=f"No existe una cancha con id '{id_cancha}'"
        ), 404)

    datos = validar_body_cancha_patch(body)

    campos = {}

    if 'nombre' in datos:
        campos['nombre'] = datos['nombre']

    if 'precio_hora' in datos:
        campos['precio_hora'] = datos['precio_hora']

    if 'techada' in datos:
        campos['techada'] = 1 if datos['techada'] else 0

    if 'activa' in datos:
        campos['activa'] = 1 if datos['activa'] else 0

    db.actualizar_cancha_parcial(id_cancha, campos)

    cancha = db.obtener_cancha_por_id(id_cancha)

    return construir_cancha_dto(cancha)


def eliminar_cancha(id_cancha: int) -> None:
    cancha = db.obtener_cancha_por_id(id_cancha)

    if not cancha:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_CANCHA_NOT_FOUND,
            message='Cancha no encontrada',
            description=f"No existe una cancha con id '{id_cancha}'"
        ), 404)

    if db.contar_reservas_por_cancha(id_cancha) > 0:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_CANCHA_HAS_RESERVAS,
            message='La cancha tiene reservas asociadas',
            description='No se puede eliminar una cancha que tiene reservas asociadas; desactívela mediante PATCH'
        ), 409)

    db.eliminar_cancha(id_cancha)


def listar_canchas_disponibles(params: dict) -> tuple[list[dict], int]:
    filas, total = db.obtener_canchas_disponibles(
        fecha=params['fecha'],
        hora_inicio=params['hora_inicio'],
        hora_fin=params['hora_fin'],
        id_deporte=params.get('id_deporte'),
        techada=params.get('techada'),
        limit=params['limit'],
        offset=params['offset']
    )

    return [construir_cancha_dto(c) for c in filas], total
