from ..constants import (
    FORMATO_FECHA,
    MIN_ID,
    ESTADOS_RESERVA,
    DEFAULT_OFFSET,
    DEFAULT_LIMIT
)
from ..utils import (
    construir_error_api,
    validar_entero,
    validar_minimo,
    validar_enum,
    validar_params_paginacion,
    validar_formato_fecha,
    parsear_fecha_hora,
    validar_estado_reserva
)


def validar_params_reservas(args: dict) -> dict:
    errores = []

    try:
        paginacion = validar_params_paginacion(args)
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    id_cancha = None
    id_socio = None
    estado = None
    fecha_desde = None
    fecha_hasta = None

    if 'id_cancha' in args:
        try:
            id_cancha = validar_minimo(validar_entero(args['id_cancha'], 'id_cancha'), MIN_ID, 'id_cancha')
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if 'id_socio' in args:
        try:
            id_socio = validar_minimo(validar_entero(args['id_socio'], 'id_socio'), MIN_ID, 'id_socio')
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if 'estado' in args:
        try:
            estado = validar_estado_reserva(args['estado'])
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if 'fecha_desde' in args:
        try:
            validar_formato_fecha(args['fecha_desde'], FORMATO_FECHA, 'fecha_desde')
            fecha_desde = args['fecha_desde']
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if 'fecha_hasta' in args:
        try:
            validar_formato_fecha(args['fecha_hasta'], FORMATO_FECHA, 'fecha_hasta')
            fecha_hasta = args['fecha_hasta']
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if fecha_desde and fecha_hasta and fecha_hasta < fecha_desde:
        errores.append(construir_error_api(
            code='invalid.fecha_rango',
            message='Rango de fechas inválido',
            description="'fecha_hasta' debe ser mayor o igual a 'fecha_desde'"
        )['errors'][0])

    if errores:
        raise ValueError({'errors': errores})

    return {
        'id_cancha': id_cancha,
        'id_socio': id_socio,
        'estado': estado,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'offset': paginacion['offset'],
        'limit': paginacion['limit']
    }


def validar_body_reserva(body: dict) -> dict:
    errores = []
    campos_requeridos = ['id_socio', 'id_cancha', 'fecha_hora_inicio', 'fecha_hora_fin']

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
        'fecha_hora_fin': fin
    }


def validar_body_estado_reserva(body: dict) -> dict:
    errores = []

    if 'estado' not in body or body['estado'] == '' or body['estado'] is None:
        errores.append(construir_error_api(
            code='required.estado',
            message="Campo requerido: 'estado'",
            description="El campo 'estado' es obligatorio"
        )['errors'][0])

    if errores:
        raise ValueError({'errors': errores})

    try:
        estado = validar_estado_reserva(body['estado'])
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    if errores:
        raise ValueError({'errors': errores})

    return {'estado': estado}


def validar_id_reserva(id_str: str) -> int:
    return validar_minimo(validar_entero(id_str, 'id'), MIN_ID, 'id')
