from datetime import datetime

from .constants import (
    ARCHIVO_DEPORTES,
    ARCHIVO_CANCHAS,
    ARCHIVO_SOCIOS,
    ARCHIVO_RESERVAS
)
from .utils import (
    cargar_csv,
    guardar_csv,
    parsear_fecha_hora,
    formatear_fecha_hora
)

ENCABEZADOS_CANCHAS  = ['ID', 'NOMBRE', 'ID_DEPORTE', 'PRECIO_HORA', 'TECHADA', 'ACTIVA']
ENCABEZADOS_SOCIOS   = ['ID', 'NOMBRE', 'EMAIL', 'ACTIVO']
ENCABEZADOS_RESERVAS = ['ID', 'ID_SOCIO', 'ID_CANCHA', 'FECHA_HORA_INICIO', 'FECHA_HORA_FIN', 'ESTADO', 'PRECIO_HORA', 'PRECIO_TOTAL']
ENCABEZADOS_DEPORTES = ['ID', 'NOMBRE']


def _normalizar_booleano_campos(campos: dict, columnas_booleanas: set) -> dict:
    """Convierte valores 0/1 o strings en booleanos para columnas booleanas."""
    normalizado = dict(campos)

    for columna in columnas_booleanas:
        if columna in normalizado:
            valor = normalizado[columna]
            if isinstance(valor, bool):
                normalizado[columna] = valor
            elif isinstance(valor, int):
                normalizado[columna] = valor == 1
            elif isinstance(valor, str):
                normalizado[columna] = valor.lower() == 'true'

    return normalizado


def _nuevo_id(registros: list[dict]) -> int:
    if not registros:
        return 1
    return max(r['id'] for r in registros) + 1


# ---------------------------------------------------------------
# Persistencia de deportes
# ---------------------------------------------------------------

def obtener_todos_los_deportes() -> list[dict]:
    return cargar_csv(ARCHIVO_DEPORTES)


def obtener_deporte_por_id(id_deporte: int) -> dict:
    deportes = obtener_todos_los_deportes()

    for deporte in deportes:
        if deporte['id'] == id_deporte:
            return deporte

    return {}


# ---------------------------------------------------------------
# Persistencia de canchas
# ---------------------------------------------------------------

def _cancha_coincide(cancha: dict, id_deporte, nombre, techada, activa) -> bool:
    if id_deporte is not None and cancha['id_deporte'] != id_deporte:
        return False

    if nombre is not None and nombre.lower() not in cancha['nombre'].lower():
        return False

    if techada is not None and cancha['techada'] != techada:
        return False

    if activa is not None and cancha['activa'] != activa:
        return False

    return True


def obtener_canchas(id_deporte=None, nombre=None, techada=None, activa=None, limit=10, offset=0) -> tuple[list[dict], int]:
    canchas = cargar_csv(ARCHIVO_CANCHAS)
    filtradas = [
        c for c in canchas
        if _cancha_coincide(c, id_deporte, nombre, techada, activa)
    ]

    total = len(filtradas)
    return filtradas[offset:offset + limit], total


def obtener_cancha_por_id(id_cancha: int) -> dict:
    canchas = cargar_csv(ARCHIVO_CANCHAS)

    for cancha in canchas:
        if cancha['id'] == id_cancha:
            return cancha

    return {}


def insertar_cancha(nombre: str, id_deporte: int, precio_hora: int, techada: bool, activa: bool) -> int:
    canchas = cargar_csv(ARCHIVO_CANCHAS)
    nuevo_id = _nuevo_id(canchas)

    canchas.append({
        'id': nuevo_id,
        'nombre': nombre,
        'id_deporte': id_deporte,
        'precio_hora': precio_hora,
        'techada': techada,
        'activa': activa
    })

    guardar_csv(ARCHIVO_CANCHAS, canchas, ENCABEZADOS_CANCHAS)
    return nuevo_id


def actualizar_cancha_parcial(id_cancha: int, campos: dict) -> None:
    canchas = cargar_csv(ARCHIVO_CANCHAS)

    for cancha in canchas:
        if cancha['id'] == id_cancha:
            campos_norm = _normalizar_booleano_campos(campos, {'techada', 'activa'})
            cancha.update(campos_norm)
            break

    guardar_csv(ARCHIVO_CANCHAS, canchas, ENCABEZADOS_CANCHAS)


def eliminar_cancha(id_cancha: int) -> bool:
    canchas = cargar_csv(ARCHIVO_CANCHAS)
    longitud_original = len(canchas)
    canchas = [c for c in canchas if c['id'] != id_cancha]

    if len(canchas) == longitud_original:
        return False

    guardar_csv(ARCHIVO_CANCHAS, canchas, ENCABEZADOS_CANCHAS)
    return True


def contar_reservas_por_cancha(id_cancha: int) -> int:
    reservas = cargar_csv(ARCHIVO_RESERVAS)
    return len([r for r in reservas if r['id_cancha'] == id_cancha])


def _reservas_superpuestas(id_cancha: int, inicio: datetime, fin: datetime, excluir_id=None) -> list[dict]:
    reservas = cargar_csv(ARCHIVO_RESERVAS)
    superpuestas = []

    for reserva in reservas:
        if reserva['id_cancha'] != id_cancha:
            continue

        if reserva['estado'] == 'cancelada':
            continue

        if excluir_id is not None and reserva['id'] == excluir_id:
            continue

        r_inicio = parsear_fecha_hora(reserva['fecha_hora_inicio'])
        r_fin = parsear_fecha_hora(reserva['fecha_hora_fin'])

        if r_inicio < fin and r_fin > inicio:
            superpuestas.append(reserva)

    return superpuestas


def obtener_canchas_disponibles(fecha: str, hora_inicio: str, hora_fin: str, id_deporte=None, techada=None, limit=10, offset=0) -> tuple[list[dict], int]:
    inicio = datetime.strptime(f"{fecha} {hora_inicio}", '%Y-%m-%d %H:%M:%S')
    fin = datetime.strptime(f"{fecha} {hora_fin}", '%Y-%m-%d %H:%M:%S')

    canchas = cargar_csv(ARCHIVO_CANCHAS)
    disponibles = []

    for cancha in canchas:
        if not cancha['activa']:
            continue

        if id_deporte is not None and cancha['id_deporte'] != id_deporte:
            continue

        if techada is not None and cancha['techada'] != techada:
            continue

        if not _reservas_superpuestas(cancha['id'], inicio, fin):
            disponibles.append(cancha)

    total = len(disponibles)
    return disponibles[offset:offset + limit], total


# ---------------------------------------------------------------
# Persistencia de socios
# ---------------------------------------------------------------

def _socio_coincide(socio: dict, nombre, activo) -> bool:
    if nombre is not None and nombre.lower() not in socio['nombre'].lower():
        return False

    if activo is not None and socio['activo'] != activo:
        return False

    return True


def obtener_todos_los_socios(nombre=None, activo=None, limit=10, offset=0) -> tuple[list[dict], int]:
    socios = cargar_csv(ARCHIVO_SOCIOS)
    filtrados = [
        s for s in socios
        if _socio_coincide(s, nombre, activo)
    ]

    total = len(filtrados)
    return filtrados[offset:offset + limit], total


def obtener_socio_por_id(id_socio: int) -> dict:
    socios = cargar_csv(ARCHIVO_SOCIOS)

    for socio in socios:
        if socio['id'] == id_socio:
            return socio

    return {}


def existe_socio_distinto(email: str, excluir_id: int) -> bool:
    socios = cargar_csv(ARCHIVO_SOCIOS)

    for socio in socios:
        if socio['email'].lower() == email.lower() and socio['id'] != excluir_id:
            return True

    return False


def insertar_socio(nombre: str, email: str) -> int:
    socios = cargar_csv(ARCHIVO_SOCIOS)
    nuevo_id = _nuevo_id(socios)

    socios.append({
        'id': nuevo_id,
        'nombre': nombre,
        'email': email,
        'activo': True
    })

    guardar_csv(ARCHIVO_SOCIOS, socios, ENCABEZADOS_SOCIOS)
    return nuevo_id


def actualizar_socio_parcial(id_socio: int, campos: dict) -> None:
    socios = cargar_csv(ARCHIVO_SOCIOS)

    for socio in socios:
        if socio['id'] == id_socio:
            campos_norm = _normalizar_booleano_campos(campos, {'activo'})
            socio.update(campos_norm)
            break

    guardar_csv(ARCHIVO_SOCIOS, socios, ENCABEZADOS_SOCIOS)


# ---------------------------------------------------------------
# Persistencia de reservas
# ---------------------------------------------------------------

def _reserva_coincide(reserva: dict, id_cancha, id_socio, estado, fecha_desde, fecha_hasta) -> bool:
    if id_cancha is not None and reserva['id_cancha'] != id_cancha:
        return False

    if id_socio is not None and reserva['id_socio'] != id_socio:
        return False

    if estado is not None and reserva['estado'] != estado:
        return False

    if fecha_desde is not None or fecha_hasta is not None:
        fecha_inicio = parsear_fecha_hora(reserva['fecha_hora_inicio']).date().isoformat()

        if fecha_desde is not None and fecha_inicio < fecha_desde:
            return False

        if fecha_hasta is not None and fecha_inicio > fecha_hasta:
            return False

    return True


def obtener_todas_las_reservas(id_cancha=None, id_socio=None, estado=None, fecha_desde=None, fecha_hasta=None, limit=10, offset=0) -> tuple[list[dict], int]:
    reservas = cargar_csv(ARCHIVO_RESERVAS)
    filtradas = [
        r for r in reservas
        if _reserva_coincide(r, id_cancha, id_socio, estado, fecha_desde, fecha_hasta)
    ]

    total = len(filtradas)
    return filtradas[offset:offset + limit], total


def obtener_reserva_por_id(id_reserva: int) -> dict:
    reservas = cargar_csv(ARCHIVO_RESERVAS)

    for reserva in reservas:
        if reserva['id'] == id_reserva:
            return reserva

    return {}


def insertar_reserva(id_socio: int, id_cancha: int, fecha_hora_inicio, fecha_hora_fin, estado: str, precio_hora: int, precio_total: int) -> int:
    reservas = cargar_csv(ARCHIVO_RESERVAS)
    nuevo_id = _nuevo_id(reservas)

    reservas.append({
        'id': nuevo_id,
        'id_socio': id_socio,
        'id_cancha': id_cancha,
        'fecha_hora_inicio': formatear_fecha_hora(fecha_hora_inicio),
        'fecha_hora_fin': formatear_fecha_hora(fecha_hora_fin),
        'estado': estado,
        'precio_hora': precio_hora,
        'precio_total': precio_total
    })

    guardar_csv(ARCHIVO_RESERVAS, reservas, ENCABEZADOS_RESERVAS)
    return nuevo_id


def insertar_reservas_batch(reservas: list[dict]) -> list[int]:
    """Inserta un lote de reservas y retorna sus ids."""
    ids = []

    for reserva in reservas:
        nuevo_id = insertar_reserva(
            reserva['id_socio'],
            reserva['id_cancha'],
            reserva['fecha_hora_inicio'],
            reserva['fecha_hora_fin'],
            reserva['estado'],
            reserva['precio_hora'],
            reserva['precio_total']
        )
        ids.append(nuevo_id)

    return ids


def actualizar_estado_reserva(id_reserva: int, estado: str) -> None:
    reservas = cargar_csv(ARCHIVO_RESERVAS)

    for reserva in reservas:
        if reserva['id'] == id_reserva:
            reserva['estado'] = estado
            break

    guardar_csv(ARCHIVO_RESERVAS, reservas, ENCABEZADOS_RESERVAS)


def existe_reserva_superpuesta(id_cancha: int, fecha_hora_inicio, fecha_hora_fin, excluir_id=None) -> bool:
    inicio = fecha_hora_inicio if isinstance(fecha_hora_inicio, datetime) else parsear_fecha_hora(fecha_hora_inicio)
    fin = fecha_hora_fin if isinstance(fecha_hora_fin, datetime) else parsear_fecha_hora(fecha_hora_fin)

    return len(_reservas_superpuestas(id_cancha, inicio, fin, excluir_id)) > 0


# ---------------------------------------------------------------
# Stub de bloqueos: la rama main no implementa bloqueos.
# ---------------------------------------------------------------

def existe_bloqueo_superpuesto_para_reserva(id_cancha: int, fecha_hora_inicio, fecha_hora_fin, excluir_id=None) -> bool:
    return False
