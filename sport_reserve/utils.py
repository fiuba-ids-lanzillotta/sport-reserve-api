from datetime import datetime, time
from re import sub
import re
import logging
from .constants import (
    FORMATO_FECHA,
    FORMATO_HORA,
    PATRON_FECHA_HORA,
    SUFIJO_ZONA_HORARIA,
    ESTADOS_RESERVA,
    ERROR_CODE_INVALID_MIN_VALUE,
    ERROR_CODE_INVALID_MAX_VALUE,
    MIN_OFFSET,
    MIN_LIMIT,
    MAX_LIMIT,
    MIN_ID,
    DEFAULT_OFFSET,
    DEFAULT_LIMIT
)

logger = logging.getLogger(__name__)


def construir_error_api(code: str, message: str, description: str, level: str = 'error') -> dict:
    return {
        'errors': [{
            'code': code,
            'message': message,
            'level': level,
            'description': description
        }]
    }


def leer_archivo(ruta: str) -> list[str]:
    try:
        # utf-8-sig descarta automáticamente el BOM si el archivo fue creado en Windows
        with open(ruta, 'r', encoding='utf-8-sig') as archivo:
            return archivo.read().splitlines()
    except IOError:
        logger.error(f"No se pudo leer el archivo: '{ruta}'")

        return []


def escribir_archivo(ruta: str, contenido: str) -> None:
    try:
        with open(ruta, 'w', encoding='utf-8') as archivo:
            archivo.write(contenido)
    except IOError:
        logger.error(f"No se pudo escribir el archivo: '{ruta}'")


def parsear_csv(lineas: list[str], separador: str = ', ') -> tuple[list[str], list[str]]:
    encabezados = []

    for encabezado in lineas[0].split(separador):
        encabezados.append(encabezado.strip().lower())

    filas = []

    for fila in lineas[1:]:
        if fila.strip():
            filas.append(fila)

    return encabezados, filas


def convertir_valor_csv(clave: str, valor: str):
    valor = valor.strip()

    if valor == '':
        return None

    if clave == 'id' or clave.startswith('id_'):
        return validar_entero(valor, clave)

    if clave in ('techada', 'activa', 'activo'):
        return valor.lower() == 'true'

    if clave.startswith('precio_'):
        return int(valor)

    return valor


def convertir_fila_a_dict(fila: str, encabezados: list[str], separador: str = ', ') -> dict:
    valores_raw = fila.split(separador)
    registro = {}

    for i, encabezado in enumerate(encabezados):
        valor = valores_raw[i].strip() if i < len(valores_raw) else ''
        registro[encabezado] = convertir_valor_csv(encabezado, valor)

    return registro


def cargar_csv(ruta: str) -> list[dict]:
    lineas = leer_archivo(ruta)

    if not lineas:
        return []

    encabezados, filas = parsear_csv(lineas)
    registros = []

    for fila in filas:
        registros.append(convertir_fila_a_dict(fila, encabezados))

    return registros


def guardar_csv(ruta: str, registros: list[dict], encabezados: list[str]) -> None:
    lineas = [', '.join(encabezados)]

    for registro in registros:
        valores = []

        for encabezado in encabezados:
            clave = encabezado.lower()
            valor = registro.get(clave, '')

            if valor is None:
                valor = ''
            elif isinstance(valor, bool):
                valor = str(valor).lower()
            else:
                valor = str(valor)

            valores.append(valor)

        lineas.append(', '.join(valores))

    escribir_archivo(ruta, '\n'.join(lineas))


def validar_formato_fecha(fecha: str, formato: str, nombre: str = 'fecha') -> datetime:
    try:
        return datetime.strptime(fecha, formato)
    except ValueError:
        logger.warning(f"Formato de fecha inválido: '{fecha}' no cumple el formato '{formato}'")

        raise ValueError(construir_error_api(
            code=f'invalid.{nombre}.format',
            message=f"Formato de '{nombre}' inválido",
            description=f"El valor '{fecha}' no cumple el formato esperado '{formato}'"
        ))


def validar_formato_hora(hora: str, nombre: str = 'hora') -> time:
    try:
        return datetime.strptime(hora, FORMATO_HORA).time()
    except ValueError:
        logger.warning(f"Formato de hora inválido: '{hora}' no cumple el formato '{FORMATO_HORA}'")

        raise ValueError(construir_error_api(
            code=f'invalid.{nombre}.format',
            message=f"Formato de '{nombre}' inválido",
            description=f"El valor '{hora}' no cumple el formato esperado '{FORMATO_HORA}'"
        ))


def parsear_fecha_hora(cadena: str, nombre: str = 'fecha_hora') -> datetime:
    if not re.match(PATRON_FECHA_HORA, cadena):
        raise ValueError(construir_error_api(
            code=f'invalid.{nombre}.format',
            message=f"Formato de '{nombre}' inválido",
            description=f"El valor '{cadena}' no cumple el formato esperado 'YYYY-MM-DDTHH:MM:SS.ffffff-03:00'"
        ))

    try:
        dt = datetime.fromisoformat(cadena)

        return dt.replace(tzinfo=None)
    except ValueError:
        raise ValueError(construir_error_api(
            code=f'invalid.{nombre}.format',
            message=f"Formato de '{nombre}' inválido",
            description=f"El valor '{cadena}' no es una fecha-hora válida"
        ))


def formatear_fecha_hora(dt) -> str:
    if isinstance(dt, str):
        return dt

    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f') + SUFIJO_ZONA_HORARIA


def validar_entero(numero: str, nombre: str = 'numero') -> int:
    numero_sin_letras = sub('[a-zA-Z]+', '', numero)

    try:
        return int(numero_sin_letras)
    except ValueError:
        logger.warning(f"Valor numérico inválido: '{numero}' no puede convertirse a entero")

        raise ValueError(construir_error_api(
            code=f'invalid.{nombre}.format',
            message=f"Formato de '{nombre}' inválido",
            description=f"El valor '{numero}' no puede convertirse a un número entero"
        ))


def validar_minimo(valor: int, minimo: int, nombre: str) -> int:
    if valor < minimo:
        logger.warning(f"Valor por debajo del mínimo: '{nombre}' es {valor}, mínimo esperado {minimo}")

        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_MIN_VALUE,
            message='Valor por debajo del mínimo permitido',
            description=f"El parámetro '{nombre}' debe ser mayor o igual a {minimo}. Se recibió: {valor}"
        ))

    return valor


def validar_maximo(valor: int, maximo: int, nombre: str) -> int:
    if valor > maximo:
        logger.warning(f"Valor por encima del máximo: '{nombre}' es {valor}, máximo esperado {maximo}")

        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_MAX_VALUE,
            message='Valor por encima del máximo permitido',
            description=f"El parámetro '{nombre}' debe ser menor o igual a {maximo}. Se recibió: {valor}"
        ))

    return valor


def validar_enum(valor: str, valores_validos: set, nombre: str) -> str:
    if valor.lower() not in valores_validos:
        logger.warning(f"Valor inválido para '{nombre}': '{valor}'")

        raise ValueError(construir_error_api(
            code=f'invalid.{nombre}',
            message=f"'{nombre}' inválido",
            description=f"El valor '{valor}' no es válido. Valores aceptados: {', '.join(sorted(valores_validos))}"
        ))

    return valor.lower()


def validar_estado_reserva(estado: str) -> str:
    return validar_enum(estado, ESTADOS_RESERVA, 'estado')


def validar_booleano(valor, nombre: str = 'booleano') -> bool:
    if isinstance(valor, bool):
        return valor

    if isinstance(valor, str):
        if valor.lower() == 'true':
            return True

        if valor.lower() == 'false':
            return False

    raise ValueError(construir_error_api(
        code=f'invalid.{nombre}.format',
        message=f"Formato de '{nombre}' inválido",
        description=f"El valor '{valor}' no es un booleano válido. Se espera 'true' o 'false'"
    ))


def validar_id(id_str: str) -> int:
    id_entero = validar_entero(id_str, 'id')

    return validar_minimo(id_entero, MIN_ID, 'id')


def validar_params_paginacion(args: dict) -> dict:
    """Valida los query params _offset y _limit. Retorna un dict con los valores validados."""
    errores = []

    offset = MIN_OFFSET
    limit = MIN_LIMIT

    try:
        offset = validar_minimo(validar_entero(args.get('_offset', DEFAULT_OFFSET), '_offset'), MIN_OFFSET, '_offset')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        limit = validar_minimo(validar_entero(args.get('_limit', DEFAULT_LIMIT), '_limit'), MIN_LIMIT, '_limit')
        limit = validar_maximo(limit, MAX_LIMIT, '_limit')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    if errores:
        raise ValueError({'errors': errores})

    return {'offset': offset, 'limit': limit}
