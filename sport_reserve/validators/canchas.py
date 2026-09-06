from ..constants import (
    FORMATO_FECHA,
    FORMATO_HORA,
    MIN_ID,
    MIN_PRECIO_HORA,
    DEFAULT_OFFSET,
    DEFAULT_LIMIT
)
from ..utils import (
    construir_error_api,
    validar_entero,
    validar_minimo,
    validar_booleano,
    validar_params_paginacion,
    validar_formato_fecha,
    validar_formato_hora
)


def validar_params_canchas(args: dict) -> dict:
    errores = []

    try:
        paginacion = validar_params_paginacion(args)
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    id_deporte = None

    if 'id_deporte' in args:
        try:
            id_deporte = validar_minimo(validar_entero(args['id_deporte'], 'id_deporte'), MIN_ID, 'id_deporte')
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    techada = None

    if 'techada' in args:
        try:
            techada = validar_booleano(args['techada'], 'techada')
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    activa = None

    if 'activa' in args:
        try:
            activa = validar_booleano(args['activa'], 'activa')
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if errores:
        raise ValueError({'errors': errores})

    return {
        'id_deporte': id_deporte,
        'nombre': args.get('nombre'),
        'techada': techada,
        'activa': activa,
        'offset': paginacion['offset'],
        'limit': paginacion['limit']
    }


def validar_params_disponibles(args: dict) -> dict:
    errores = []

    try:
        paginacion = validar_params_paginacion(args)
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    fecha = None
    hora_inicio = None
    hora_fin = None
    id_deporte = None
    techada = None

    if 'fecha' not in args or not args['fecha']:
        errores.append(construir_error_api(
            code='required.fecha',
            message="Campo requerido: 'fecha'",
            description="El parámetro 'fecha' es obligatorio para consultar disponibilidad"
        )['errors'][0])
    else:
        try:
            validar_formato_fecha(args['fecha'], FORMATO_FECHA, 'fecha')
            fecha = args['fecha']
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if 'hora_inicio' not in args or not args['hora_inicio']:
        errores.append(construir_error_api(
            code='required.hora_inicio',
            message="Campo requerido: 'hora_inicio'",
            description="El parámetro 'hora_inicio' es obligatorio para consultar disponibilidad"
        )['errors'][0])
    else:
        try:
            validar_formato_hora(args['hora_inicio'], 'hora_inicio')
            hora_inicio = args['hora_inicio']
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if 'hora_fin' not in args or not args['hora_fin']:
        errores.append(construir_error_api(
            code='required.hora_fin',
            message="Campo requerido: 'hora_fin'",
            description="El parámetro 'hora_fin' es obligatorio para consultar disponibilidad"
        )['errors'][0])
    else:
        try:
            validar_formato_hora(args['hora_fin'], 'hora_fin')
            hora_fin = args['hora_fin']
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if fecha and hora_inicio and hora_fin:
        if hora_fin <= hora_inicio:
            errores.append(construir_error_api(
                code='invalid.hora_fin',
                message='El horario de fin debe ser posterior al de inicio',
                description="'hora_fin' debe ser mayor a 'hora_inicio'"
            )['errors'][0])

    if 'id_deporte' in args:
        try:
            id_deporte = validar_minimo(validar_entero(args['id_deporte'], 'id_deporte'), MIN_ID, 'id_deporte')
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if 'techada' in args:
        try:
            techada = validar_booleano(args['techada'], 'techada')
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if errores:
        raise ValueError({'errors': errores})

    return {
        'fecha': fecha,
        'hora_inicio': hora_inicio,
        'hora_fin': hora_fin,
        'id_deporte': id_deporte,
        'techada': techada,
        'offset': paginacion['offset'],
        'limit': paginacion['limit']
    }


def validar_body_cancha(body: dict) -> dict:
    errores = []
    campos_requeridos = ['nombre', 'id_deporte', 'precio_hora']

    for campo in campos_requeridos:
        if campo not in body or body[campo] == '' or body[campo] is None:
            errores.append(construir_error_api(
                code=f'required.{campo}',
                message=f"Campo requerido: '{campo}'",
                description=f"El campo '{campo}' es obligatorio y no puede estar vacío"
            )['errors'][0])

    if errores:
        raise ValueError({'errors': errores})

    id_deporte = None
    precio_hora = None

    try:
        id_deporte = validar_minimo(validar_entero(str(body['id_deporte']), 'id_deporte'), MIN_ID, 'id_deporte')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        precio_hora = validar_minimo(validar_entero(str(body['precio_hora']), 'precio_hora'), MIN_PRECIO_HORA, 'precio_hora')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    techada = body.get('techada', False)
    activa = body.get('activa', True)

    try:
        techada = validar_booleano(techada, 'techada')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        activa = validar_booleano(activa, 'activa')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    if errores:
        raise ValueError({'errors': errores})

    return {
        'nombre': str(body['nombre']).strip(),
        'id_deporte': id_deporte,
        'precio_hora': precio_hora,
        'techada': techada,
        'activa': activa
    }


def validar_body_cancha_patch(body: dict) -> dict:
    campos_conocidos = {'nombre', 'precio_hora', 'techada', 'activa'}
    campos_presentes = {k for k in body if k in campos_conocidos and body[k] != '' and body[k] is not None}

    if not campos_presentes:
        raise ValueError(construir_error_api(
            code='invalid.body',
            message='Cuerpo de la solicitud inválido',
            description='El cuerpo debe contener al menos un campo válido y no vacío: nombre, precio_hora, techada o activa'
        ))

    errores = []
    datos = {}

    if 'nombre' in campos_presentes:
        datos['nombre'] = str(body['nombre']).strip()

    if 'precio_hora' in campos_presentes:
        try:
            datos['precio_hora'] = validar_minimo(validar_entero(str(body['precio_hora']), 'precio_hora'), MIN_PRECIO_HORA, 'precio_hora')
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if 'techada' in campos_presentes:
        try:
            datos['techada'] = validar_booleano(body['techada'], 'techada')
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if 'activa' in campos_presentes:
        try:
            datos['activa'] = validar_booleano(body['activa'], 'activa')
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if errores:
        raise ValueError({'errors': errores})

    return datos


def validar_id_cancha(id_str: str) -> int:
    return validar_minimo(validar_entero(id_str, 'id'), MIN_ID, 'id')
