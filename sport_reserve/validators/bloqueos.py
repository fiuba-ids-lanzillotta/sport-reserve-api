from ..constants import (
    FORMATO_FECHA,
    FORMATO_HORA,
    MIN_ID,
    DEFAULT_OFFSET,
    DEFAULT_LIMIT
)
from ..utils import (
    construir_error_api,
    validar_entero,
    validar_minimo,
    validar_params_paginacion,
    validar_formato_fecha,
    validar_formato_hora
)


def validar_params_bloqueos(args: dict) -> dict:
    errores = []

    try:
        paginacion = validar_params_paginacion(args)
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    id_cancha = None
    fecha = None

    if 'id_cancha' in args:
        try:
            id_cancha = validar_minimo(validar_entero(args['id_cancha'], 'id_cancha'), MIN_ID, 'id_cancha')
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if 'fecha' in args:
        try:
            validar_formato_fecha(args['fecha'], FORMATO_FECHA, 'fecha')
            fecha = args['fecha']
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if errores:
        raise ValueError({'errors': errores})

    return {
        'id_cancha': id_cancha,
        'fecha': fecha,
        'offset': paginacion['offset'],
        'limit': paginacion['limit']
    }


def validar_body_bloqueo(body: dict) -> dict:
    errores = []
    campos_requeridos = ['id_cancha', 'fecha', 'hora_inicio', 'hora_fin', 'motivo']

    for campo in campos_requeridos:
        if campo not in body or body[campo] == '' or body[campo] is None:
            errores.append(construir_error_api(
                code=f'required.{campo}',
                message=f"Campo requerido: '{campo}'",
                description=f"El campo '{campo}' es obligatorio y no puede estar vacío"
            )['errors'][0])

    if errores:
        raise ValueError({'errors': errores})

    id_cancha = None
    fecha = None
    hora_inicio = None
    hora_fin = None

    try:
        id_cancha = validar_minimo(validar_entero(str(body['id_cancha']), 'id_cancha'), MIN_ID, 'id_cancha')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        validar_formato_fecha(body['fecha'], FORMATO_FECHA, 'fecha')
        fecha = body['fecha']
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        validar_formato_hora(body['hora_inicio'], 'hora_inicio')
        hora_inicio = body['hora_inicio']
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        validar_formato_hora(body['hora_fin'], 'hora_fin')
        hora_fin = body['hora_fin']
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    if hora_inicio and hora_fin and hora_fin <= hora_inicio:
        errores.append(construir_error_api(
            code='invalid.hora_fin',
            message='La hora de fin debe ser posterior a la de inicio',
            description="'hora_fin' debe ser mayor a 'hora_inicio'"
        )['errors'][0])

    if errores:
        raise ValueError({'errors': errores})

    return {
        'id_cancha': id_cancha,
        'fecha': fecha,
        'hora_inicio': hora_inicio,
        'hora_fin': hora_fin,
        'motivo': str(body['motivo']).strip()
    }


def validar_id_bloqueo(id_str: str) -> int:
    return validar_minimo(validar_entero(id_str, 'id'), MIN_ID, 'id')
