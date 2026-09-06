import re
from ..constants import MIN_ID, DEFAULT_OFFSET, DEFAULT_LIMIT
from ..utils import (
    construir_error_api,
    validar_entero,
    validar_minimo,
    validar_booleano,
    validar_params_paginacion
)


def validar_params_socios(args: dict) -> dict:
    errores = []

    try:
        paginacion = validar_params_paginacion(args)
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    activo = None

    if 'activo' in args:
        try:
            activo = validar_booleano(args['activo'], 'activo')
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if errores:
        raise ValueError({'errors': errores})

    return {
        'nombre': args.get('nombre'),
        'activo': activo,
        'offset': paginacion['offset'],
        'limit': paginacion['limit']
    }


def _validar_email(email: str) -> bool:
    patron_email = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(patron_email, email) is not None


def _validar_nombre(nombre: str) -> bool:
    patron_nombre = r'^[A-Za-zÀ-ÿ]+(?: [A-Za-zÀ-ÿ]+)*$'
    return re.match(patron_nombre, nombre) is not None


def validar_body_socio(body: dict) -> dict:
    errores = []

    for campo in ['nombre', 'email']:
        if campo not in body or not str(body.get(campo, '')).strip():
            errores.append(construir_error_api(
                code=f'required.{campo}',
                message=f"Campo requerido: '{campo}'",
                description=f"El campo '{campo}' es obligatorio y no puede estar vacío"
            )['errors'][0])

    if errores:
        raise ValueError({'errors': errores})

    nombre = str(body['nombre']).strip()
    email = str(body['email']).strip()

    if not _validar_nombre(nombre):
        errores.append(construir_error_api(
            code='invalid.nombre.format',
            message="Formato de 'nombre' inválido",
            description="El nombre solo puede contener letras y espacios simples entre palabras"
        )['errors'][0])

    if not _validar_email(email):
        errores.append(construir_error_api(
            code='invalid.email.format',
            message="Formato de 'email' inválido",
            description=f"El valor '{email}' no tiene un formato de correo electrónico válido"
        )['errors'][0])

    if errores:
        raise ValueError({'errors': errores})

    return {'nombre': nombre, 'email': email}


def validar_body_socio_patch(body: dict) -> dict:
    campos_conocidos = {'nombre', 'email', 'activo'}
    campos_presentes = {k for k in body if k in campos_conocidos and body[k] != '' and body[k] is not None}

    if not campos_presentes:
        raise ValueError(construir_error_api(
            code='invalid.body',
            message='Cuerpo de la solicitud inválido',
            description='El cuerpo debe contener al menos un campo válido y no vacío: nombre, email o activo'
        ))

    errores = []
    datos = {}

    if 'nombre' in campos_presentes:
        nombre = str(body['nombre']).strip()

        if not _validar_nombre(nombre):
            errores.append(construir_error_api(
                code='invalid.nombre.format',
                message="Formato de 'nombre' inválido",
                description="El nombre solo puede contener letras y espacios simples entre palabras"
            )['errors'][0])
        else:
            datos['nombre'] = nombre

    if 'email' in campos_presentes:
        email = str(body['email']).strip()

        if not _validar_email(email):
            errores.append(construir_error_api(
                code='invalid.email.format',
                message="Formato de 'email' inválido",
                description=f"El valor '{email}' no tiene un formato de correo electrónico válido"
            )['errors'][0])
        else:
            datos['email'] = email

    if 'activo' in campos_presentes:
        try:
            datos['activo'] = validar_booleano(body['activo'], 'activo')
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if errores:
        raise ValueError({'errors': errores})

    return datos


def validar_id_socio(id_str: str) -> int:
    return validar_minimo(validar_entero(id_str, 'id'), MIN_ID, 'id')
