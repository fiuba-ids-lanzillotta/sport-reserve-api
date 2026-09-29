from sqlalchemy import create_engine, text
from .constants import DB_URL

# Motor de conexión compartido por toda la aplicación.
motor = create_engine(DB_URL, pool_pre_ping=True)


def fila_a_dict(fila) -> dict:
    """Convierte una fila del resultado de una query en un diccionario."""
    return dict(fila._mapping)


def ejecutar_consulta(sql: str, parametros: dict = None) -> list[dict]:
    """Ejecuta una SELECT y devuelve todas las filas como lista de dicts."""
    with motor.connect() as conexion:
        resultado = conexion.execute(text(sql), parametros or {})

        return [fila_a_dict(fila) for fila in resultado]


def ejecutar_mutacion(sql: str, parametros: dict = None) -> int:
    """
    Ejecuta un INSERT, UPDATE o DELETE y hace commit.
    Retorna el id generado en caso de INSERT, o 0 en otro caso.
    """
    with motor.begin() as conexion:
        resultado = conexion.execute(text(sql), parametros or {})

        return resultado.lastrowid or 0


# ---------------------------------------------------------------
# Queries de deportes
# ---------------------------------------------------------------

def obtener_todos_los_deportes() -> list[dict]:
    return ejecutar_consulta('SELECT id, nombre FROM deportes ORDER BY id')


def obtener_deporte_por_id(id_deporte: int) -> dict:
    filas = ejecutar_consulta('SELECT id, nombre FROM deportes WHERE id = :id', {'id': id_deporte})

    return filas[0] if filas else {}


# ---------------------------------------------------------------
# Queries de canchas
# ---------------------------------------------------------------

def _where_canchas(id_deporte, nombre, techada, activa):
    where = []
    params = {}

    if id_deporte is not None:
        where.append('id_deporte = :id_deporte')
        params['id_deporte'] = id_deporte

    if nombre is not None:
        where.append('LOWER(nombre) LIKE LOWER(:nombre)')
        params['nombre'] = f'%{nombre}%'

    if techada is not None:
        where.append('techada = :techada')
        params['techada'] = 1 if techada else 0

    if activa is not None:
        where.append('activa = :activa')
        params['activa'] = 1 if activa else 0

    return where, params


def obtener_canchas(id_deporte=None, nombre=None, techada=None, activa=None, limit=10, offset=0) -> tuple[list[dict], int]:
    where, params = _where_canchas(id_deporte, nombre, techada, activa)
    sql_where = 'WHERE ' + ' AND '.join(where) if where else ''

    sql_total = f'SELECT COUNT(*) AS total FROM canchas {sql_where}'
    total = ejecutar_consulta(sql_total, params)[0]['total']

    sql = f'SELECT id, nombre, id_deporte, precio_hora, techada, activa FROM canchas {sql_where} ORDER BY id LIMIT :limit OFFSET :offset'
    params['limit'] = limit
    params['offset'] = offset

    filas = ejecutar_consulta(sql, params)

    return filas, total


def obtener_cancha_por_id(id_cancha: int) -> dict:
    filas = ejecutar_consulta(
        'SELECT id, nombre, id_deporte, precio_hora, techada, activa FROM canchas WHERE id = :id',
        {'id': id_cancha}
    )

    return filas[0] if filas else {}


def insertar_cancha(nombre: str, id_deporte: int, precio_hora: int, techada: bool, activa: bool) -> int:
    sql = """
        INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
        VALUES (:nombre, :id_deporte, :precio_hora, :techada, :activa)
    """
    return ejecutar_mutacion(sql, {
        'nombre': nombre,
        'id_deporte': id_deporte,
        'precio_hora': precio_hora,
        'techada': 1 if techada else 0,
        'activa': 1 if activa else 0
    })


def actualizar_cancha_parcial(id_cancha: int, campos: dict) -> None:
    set_clause = ', '.join(f'{k} = :{k}' for k in campos)
    sql = f'UPDATE canchas SET {set_clause} WHERE id = :id'

    parametros = dict(campos)
    parametros['id'] = id_cancha

    ejecutar_mutacion(sql, parametros)


def eliminar_cancha(id_cancha: int) -> bool:
    filas = ejecutar_consulta('SELECT id FROM canchas WHERE id = :id', {'id': id_cancha})

    if not filas:
        return False

    ejecutar_mutacion('DELETE FROM canchas WHERE id = :id', {'id': id_cancha})

    return True


def contar_reservas_por_cancha(id_cancha: int) -> int:
    sql = 'SELECT COUNT(*) AS total FROM reservas WHERE id_cancha = :id_cancha'
    filas = ejecutar_consulta(sql, {'id_cancha': id_cancha})

    return filas[0]['total']


def obtener_canchas_disponibles(fecha: str, hora_inicio: str, hora_fin: str, id_deporte=None, techada=None, limit=10, offset=0) -> tuple[list[dict], int]:
    where = ['c.activa = 1']
    params = {'fecha': fecha, 'hora_inicio': hora_inicio, 'hora_fin': hora_fin}

    if id_deporte is not None:
        where.append('c.id_deporte = :id_deporte')
        params['id_deporte'] = id_deporte

    if techada is not None:
        where.append('c.techada = :techada')
        params['techada'] = 1 if techada else 0

    sql_where = ' AND '.join(where)

    sql_total = f"""
        SELECT COUNT(*) AS total
        FROM canchas c
        WHERE {sql_where}
          AND NOT EXISTS (
              SELECT 1 FROM reservas r
              WHERE r.id_cancha = c.id
                AND r.estado != 'cancelada'
                AND r.fecha_hora_inicio < :fecha_hora_fin
                AND r.fecha_hora_fin > :fecha_hora_inicio
          )
    """

    parametros_total = {
        'fecha_hora_inicio': f'{fecha} {hora_inicio}',
        'fecha_hora_fin': f'{fecha} {hora_fin}'
    }

    if id_deporte is not None:
        parametros_total['id_deporte'] = id_deporte

    if techada is not None:
        parametros_total['techada'] = 1 if techada else 0

    total = ejecutar_consulta(sql_total, parametros_total)[0]['total']

    sql = f"""
        SELECT c.id, c.nombre, c.id_deporte, c.precio_hora, c.techada, c.activa
        FROM canchas c
        WHERE {sql_where}
          AND NOT EXISTS (
              SELECT 1 FROM reservas r
              WHERE r.id_cancha = c.id
                AND r.estado != 'cancelada'
                AND r.fecha_hora_inicio < :fecha_hora_fin
                AND r.fecha_hora_fin > :fecha_hora_inicio
          )
        ORDER BY c.id
        LIMIT :limit OFFSET :offset
    """

    params['limit'] = limit
    params['offset'] = offset
    params['fecha_hora_inicio'] = f'{fecha} {hora_inicio}'
    params['fecha_hora_fin'] = f'{fecha} {hora_fin}'

    filas = ejecutar_consulta(sql, params)

    return filas, total


# ---------------------------------------------------------------
# Queries de socios
# ---------------------------------------------------------------

def _where_socios(nombre, activo):
    where = []
    params = {}

    if nombre is not None:
        where.append('LOWER(nombre) LIKE LOWER(:nombre)')
        params['nombre'] = f'%{nombre}%'

    if activo is not None:
        where.append('activo = :activo')
        params['activo'] = 1 if activo else 0

    return where, params


def obtener_todos_los_socios(nombre=None, activo=None, limit=10, offset=0) -> tuple[list[dict], int]:
    where, params = _where_socios(nombre, activo)
    sql_where = 'WHERE ' + ' AND '.join(where) if where else ''

    sql_total = f'SELECT COUNT(*) AS total FROM socios {sql_where}'
    total = ejecutar_consulta(sql_total, params)[0]['total']

    sql = f'SELECT id, nombre, email, activo FROM socios {sql_where} ORDER BY id LIMIT :limit OFFSET :offset'
    params['limit'] = limit
    params['offset'] = offset

    filas = ejecutar_consulta(sql, params)

    return filas, total


def obtener_socio_por_id(id_socio: int) -> dict:
    filas = ejecutar_consulta('SELECT id, nombre, email, activo FROM socios WHERE id = :id', {'id': id_socio})

    return filas[0] if filas else {}


def existe_socio_distinto(email: str, excluir_id: int) -> bool:
    sql = 'SELECT id FROM socios WHERE email = :email AND id != :excluir_id LIMIT 1'
    filas = ejecutar_consulta(sql, {'email': email, 'excluir_id': excluir_id})

    return len(filas) > 0


def insertar_socio(nombre: str, email: str) -> int:
    sql = 'INSERT INTO socios (nombre, email) VALUES (:nombre, :email)'

    return ejecutar_mutacion(sql, {'nombre': nombre, 'email': email})


def actualizar_socio_parcial(id_socio: int, campos: dict) -> None:
    set_clause = ', '.join(f'{k} = :{k}' for k in campos)
    sql = f'UPDATE socios SET {set_clause} WHERE id = :id'

    parametros = dict(campos)
    parametros['id'] = id_socio

    ejecutar_mutacion(sql, parametros)


# ---------------------------------------------------------------
# Queries de reservas
# ---------------------------------------------------------------

def _where_reservas(id_cancha, id_socio, estado, fecha_desde, fecha_hasta):
    where = []
    params = {}

    if id_cancha is not None:
        where.append('r.id_cancha = :id_cancha')
        params['id_cancha'] = id_cancha

    if id_socio is not None:
        where.append('r.id_socio = :id_socio')
        params['id_socio'] = id_socio

    if estado is not None:
        where.append('r.estado = :estado')
        params['estado'] = estado

    if fecha_desde is not None:
        where.append('DATE(r.fecha_hora_inicio) >= :fecha_desde')
        params['fecha_desde'] = fecha_desde

    if fecha_hasta is not None:
        where.append('DATE(r.fecha_hora_inicio) <= :fecha_hasta')
        params['fecha_hasta'] = fecha_hasta

    return where, params


def obtener_todas_las_reservas(id_cancha=None, id_socio=None, estado=None, fecha_desde=None, fecha_hasta=None, limit=10, offset=0) -> tuple[list[dict], int]:
    where, params = _where_reservas(id_cancha, id_socio, estado, fecha_desde, fecha_hasta)
    sql_where = 'WHERE ' + ' AND '.join(where) if where else ''

    sql_total = f'SELECT COUNT(*) AS total FROM reservas r {sql_where}'
    total = ejecutar_consulta(sql_total, params)[0]['total']

    sql = f"""
        SELECT id, id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, precio_total
        FROM reservas r
        {sql_where}
        ORDER BY r.id
        LIMIT :limit OFFSET :offset
    """
    params['limit'] = limit
    params['offset'] = offset

    filas = ejecutar_consulta(sql, params)

    return filas, total


def obtener_reserva_por_id(id_reserva: int) -> dict:
    filas = ejecutar_consulta(
        'SELECT id, id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, precio_total FROM reservas WHERE id = :id',
        {'id': id_reserva}
    )

    return filas[0] if filas else {}


def insertar_reserva(id_socio: int, id_cancha: int, fecha_hora_inicio, fecha_hora_fin, estado: str, precio_hora: int, precio_total: int) -> int:
    sql = """
        INSERT INTO reservas (id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, precio_total)
        VALUES (:id_socio, :id_cancha, :fecha_hora_inicio, :fecha_hora_fin, :estado, :precio_hora, :precio_total)
    """
    return ejecutar_mutacion(sql, {
        'id_socio': id_socio,
        'id_cancha': id_cancha,
        'fecha_hora_inicio': fecha_hora_inicio,
        'fecha_hora_fin': fecha_hora_fin,
        'estado': estado,
        'precio_hora': precio_hora,
        'precio_total': precio_total
    })


def insertar_reservas_batch(reservas: list[dict]) -> list[int]:
    """Inserta un lote de reservas dentro de una transacción y retorna sus ids."""
    sql = """
        INSERT INTO reservas (id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, precio_total)
        VALUES (:id_socio, :id_cancha, :fecha_hora_inicio, :fecha_hora_fin, :estado, :precio_hora, :precio_total)
    """

    ids = []

    with motor.begin() as conexion:
        for reserva in reservas:
            resultado = conexion.execute(text(sql), reserva)
            ids.append(resultado.lastrowid or 0)

    return ids


def actualizar_estado_reserva(id_reserva: int, estado: str) -> None:
    sql = 'UPDATE reservas SET estado = :estado WHERE id = :id'
    ejecutar_mutacion(sql, {'estado': estado, 'id': id_reserva})


def existe_reserva_superpuesta(id_cancha: int, fecha_hora_inicio, fecha_hora_fin, excluir_id=None) -> bool:
    sql = """
        SELECT 1 FROM reservas
        WHERE id_cancha = :id_cancha
          AND estado != 'cancelada'
          AND fecha_hora_inicio < :fecha_hora_fin
          AND fecha_hora_fin > :fecha_hora_inicio
    """
    params = {
        'id_cancha': id_cancha,
        'fecha_hora_inicio': fecha_hora_inicio,
        'fecha_hora_fin': fecha_hora_fin
    }

    if excluir_id is not None:
        sql += ' AND id != :excluir_id'
        params['excluir_id'] = excluir_id

    sql += ' LIMIT 1'

    filas = ejecutar_consulta(sql, params)

    return len(filas) > 0

