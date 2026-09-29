from ..constants import (
    ERROR_CODE_SOCIO_NOT_FOUND,
    ERROR_CODE_SOCIO_EXISTS
)
from ..utils import construir_error_api
from ..validators.socios import (
    validar_body_socio,
    validar_body_socio_patch
)
from .. import db


def construir_socio_dto(socio: dict) -> dict:
    return {
        'id': socio['id'],
        'nombre': socio['nombre'],
        'email': socio['email'],
        'activo': bool(socio['activo'])
    }


def listar_socios(params: dict) -> tuple[list[dict], int]:
    filas, total = db.obtener_todos_los_socios(
        nombre=params.get('nombre'),
        activo=params.get('activo'),
        limit=params['limit'],
        offset=params['offset']
    )

    return [construir_socio_dto(s) for s in filas], total


def crear_socio(body: dict) -> dict:
    datos = validar_body_socio(body)

    if db.existe_socio_distinto(datos['email'], excluir_id=0):
        raise ValueError(construir_error_api(
            code=ERROR_CODE_SOCIO_EXISTS,
            message='El socio ya existe',
            description=f"Ya existe un socio registrado con el email '{datos['email']}'"
        ), 409)

    nuevo_id = db.insertar_socio(datos['nombre'], datos['email'])
    socio = db.obtener_socio_por_id(nuevo_id)

    return construir_socio_dto(socio)


def buscar_socio_por_id(id_socio: int) -> dict:
    socio = db.obtener_socio_por_id(id_socio)

    if not socio:
        return {}

    return construir_socio_dto(socio)


def actualizar_socio_parcial(id_socio: int, body: dict) -> dict:
    socio = db.obtener_socio_por_id(id_socio)

    if not socio:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_SOCIO_NOT_FOUND,
            message='Socio no encontrado',
            description=f"No existe un socio con id '{id_socio}'"
        ), 404)

    datos = validar_body_socio_patch(body)
    campos = {}

    if 'nombre' in datos:
        campos['nombre'] = datos['nombre']

    if 'email' in datos:
        if db.existe_socio_distinto(datos['email'], excluir_id=id_socio):
            raise ValueError(construir_error_api(
                code=ERROR_CODE_SOCIO_EXISTS,
                message='El socio ya existe',
                description=f"Ya existe otro socio registrado con el email '{datos['email']}'"
            ), 409)
        campos['email'] = datos['email']

    if 'activo' in datos:
        campos['activo'] = 1 if datos['activo'] else 0

    db.actualizar_socio_parcial(id_socio, campos)

    socio = db.obtener_socio_por_id(id_socio)

    return construir_socio_dto(socio)
