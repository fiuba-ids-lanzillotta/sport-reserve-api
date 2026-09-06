from ..constants import (
    MIN_ID,
    MIN_CANTIDAD_SEMANAS,
    MAX_CANTIDAD_SEMANAS
)
from ..utils import (
    construir_error_api,
    validar_entero,
    validar_minimo,
    validar_maximo,
    parsear_fecha_hora
)


def validar_body_reserva_recurrente(body: dict) -> dict:
    errores = []
    campos_requeridos = ['id_socio', 'id_cancha', 'fecha_hora_inicio', 'fecha_hora_fin', 'cantidad_semanas']

    for campo in campos_requeridos:
        if campo not in body or body[campo] == '' or body[campo] is None:
            errores.append(construir_error_api(
                code=f'required.{campo}',
                message=f"Campo requerido: '{campo}'",
                description=f"El campo '{campo}' es obligatorio y no puede estar vacío"
            )['errors'][0])

    if errores:
        raise ValueError({'errors': errores})

    id_socio = None
    id_cancha = None
    inicio = None
    fin = None
    cantidad_semanas = None

    try:
        id_socio = validar_minimo(validar_entero(str(body['id_socio']), 'id_socio'), MIN_ID, 'id_socio')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        id_cancha = validar_minimo(validar_entero(str(body['id_cancha']), 'id_cancha'), MIN_ID, 'id_cancha')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        inicio = parsear_fecha_hora(body['fecha_hora_inicio'], 'fecha_hora_inicio')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        fin = parsear_fecha_hora(body['fecha_hora_fin'], 'fecha_hora_fin')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        cantidad_semanas = validar_entero(str(body['cantidad_semanas']), 'cantidad_semanas')
        cantidad_semanas = validar_minimo(cantidad_semanas, MIN_CANTIDAD_SEMANAS, 'cantidad_semanas')
        cantidad_semanas = validar_maximo(cantidad_semanas, MAX_CANTIDAD_SEMANAS, 'cantidad_semanas')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    if inicio and fin and fin <= inicio:
        errores.append(construir_error_api(
            code='invalid.fecha_hora_fin',
            message='El horario de fin debe ser posterior al de inicio',
            description="'fecha_hora_fin' debe ser mayor a 'fecha_hora_inicio'"
        )['errors'][0])

    if errores:
        raise ValueError({'errors': errores})

    return {
        'id_socio': id_socio,
        'id_cancha': id_cancha,
        'fecha_hora_inicio': inicio,
        'fecha_hora_fin': fin,
        'cantidad_semanas': cantidad_semanas
    }
