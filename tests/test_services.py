import datetime as dt
import pytest

from sport_reserve import db
from sport_reserve.services import deportes, canchas, socios, reservas


def _codigos(excepcion):
    """Extrae los códigos de error de un ValueError de la API."""
    return [error['code'] for error in excepcion.value.args[0]['errors']]


def _status(excepcion):
    """Extrae el status HTTP de un ValueError de la API."""
    return excepcion.value.args[1] if len(excepcion.value.args) > 1 else 400


class _DatetimeFijo:
    """Sustituto de la clase datetime para devolver un 'now' determinista."""

    def __init__(self, valor):
        self.valor = valor

    def now(self):
        return self.valor


# --- deportes ---

def test_listar_deportes(monkeypatch):
    monkeypatch.setattr(db, 'obtener_todos_los_deportes', lambda: [
        {'id': 1, 'nombre': 'Fútbol'},
        {'id': 2, 'nombre': 'Básquet'}
    ])

    resultado = deportes.listar_deportes()

    assert resultado == [{'id': 1, 'nombre': 'Fútbol'}, {'id': 2, 'nombre': 'Básquet'}]


# --- canchas ---

def _cancha_encontrada(cancha_id=1):
    return {
        'id': cancha_id,
        'nombre': 'Cancha A',
        'id_deporte': 1,
        'precio_hora': 1000,
        'techada': 0,
        'activa': 1
    }


def test_listar_canchas(monkeypatch):
    monkeypatch.setattr(db, 'obtener_canchas', lambda **kwargs: ([_cancha_encontrada()], 1))

    filas, total = canchas.listar_canchas({
        'id_deporte': None,
        'nombre': None,
        'techada': None,
        'activa': None,
        'offset': 0,
        'limit': 10
    })

    assert total == 1
    assert filas[0]['techada'] is False
    assert filas[0]['activa'] is True


def test_crear_cancha_ok(monkeypatch):
    monkeypatch.setattr(db, 'obtener_deporte_por_id', lambda id_deporte: {'id': 1, 'nombre': 'Fútbol'})
    monkeypatch.setattr(db, 'insertar_cancha', lambda *args: 5)
    monkeypatch.setattr(db, 'obtener_cancha_por_id', lambda cancha_id: _cancha_encontrada(cancha_id))

    resultado = canchas.crear_cancha({
        'nombre': 'Cancha A',
        'id_deporte': 1,
        'precio_hora': 1000
    })

    assert resultado['id'] == 5
    assert resultado['precio_hora'] == 1000


def test_crear_cancha_deporte_no_encontrado(monkeypatch):
    monkeypatch.setattr(db, 'obtener_deporte_por_id', lambda id_deporte: {})

    with pytest.raises(ValueError) as excepcion:
        canchas.crear_cancha({'nombre': 'Cancha A', 'id_deporte': 99, 'precio_hora': 1000})

    assert _codigos(excepcion) == ['deporte.not.found']
    assert _status(excepcion) == 404


def test_buscar_cancha_por_id(monkeypatch):
    monkeypatch.setattr(db, 'obtener_cancha_por_id', lambda cancha_id: _cancha_encontrada(cancha_id))

    assert canchas.buscar_cancha_por_id(1)['id'] == 1


def test_buscar_cancha_por_id_no_encontrada(monkeypatch):
    monkeypatch.setattr(db, 'obtener_cancha_por_id', lambda cancha_id: {})

    assert canchas.buscar_cancha_por_id(99) == {}


def test_actualizar_cancha_parcial(monkeypatch):
    cancha = _cancha_encontrada(1)
    monkeypatch.setattr(db, 'obtener_cancha_por_id', lambda cancha_id: cancha)
    monkeypatch.setattr(db, 'actualizar_cancha_parcial', lambda cancha_id, campos: cancha.update(campos))

    resultado = canchas.actualizar_cancha_parcial(1, {'nombre': 'Cancha B', 'precio_hora': 2000})

    assert resultado['nombre'] == 'Cancha B'
    assert resultado['precio_hora'] == 2000


def test_actualizar_cancha_parcial_no_encontrada(monkeypatch):
    monkeypatch.setattr(db, 'obtener_cancha_por_id', lambda cancha_id: {})

    with pytest.raises(ValueError) as excepcion:
        canchas.actualizar_cancha_parcial(99, {'nombre': 'Cancha B'})

    assert _codigos(excepcion) == ['cancha.not.found']
    assert _status(excepcion) == 404


def test_eliminar_cancha_ok(monkeypatch):
    monkeypatch.setattr(db, 'obtener_cancha_por_id', lambda cancha_id: _cancha_encontrada(cancha_id))
    monkeypatch.setattr(db, 'contar_reservas_por_cancha', lambda cancha_id: 0)
    monkeypatch.setattr(db, 'eliminar_cancha', lambda cancha_id: True)

    assert canchas.eliminar_cancha(1) is None


def test_eliminar_cancha_con_reservas(monkeypatch):
    monkeypatch.setattr(db, 'obtener_cancha_por_id', lambda cancha_id: _cancha_encontrada(cancha_id))
    monkeypatch.setattr(db, 'contar_reservas_por_cancha', lambda cancha_id: 2)

    with pytest.raises(ValueError) as excepcion:
        canchas.eliminar_cancha(1)

    assert _codigos(excepcion) == ['cancha.has.reservas']
    assert _status(excepcion) == 409


def test_listar_canchas_disponibles(monkeypatch):
    monkeypatch.setattr(db, 'obtener_canchas_disponibles', lambda **kwargs: ([_cancha_encontrada()], 1))

    filas, total = canchas.listar_canchas_disponibles({
        'fecha': '2026-08-17',
        'hora_inicio': '10:00:00',
        'hora_fin': '12:00:00',
        'offset': 0,
        'limit': 10
    })

    assert total == 1
    assert filas[0]['id'] == 1


# --- socios ---

def _socio_encontrado(socio_id=1):
    return {'id': socio_id, 'nombre': 'Juan', 'email': 'juan@example.com', 'activo': 1}


def test_listar_socios(monkeypatch):
    monkeypatch.setattr(db, 'obtener_todos_los_socios', lambda **kwargs: ([_socio_encontrado()], 1))

    filas, total = socios.listar_socios({
        'nombre': None,
        'activo': None,
        'offset': 0,
        'limit': 10
    })

    assert total == 1
    assert filas[0]['activo'] is True


def test_crear_socio_ok(monkeypatch):
    monkeypatch.setattr(db, 'existe_socio_distinto', lambda email, excluir_id: False)
    monkeypatch.setattr(db, 'insertar_socio', lambda nombre, email: 3)
    monkeypatch.setattr(db, 'obtener_socio_por_id', lambda socio_id: _socio_encontrado(3))

    resultado = socios.crear_socio({'nombre': 'Juan', 'email': 'juan@example.com'})

    assert resultado['id'] == 3
    assert resultado['email'] == 'juan@example.com'


def test_crear_socio_duplicado(monkeypatch):
    monkeypatch.setattr(db, 'existe_socio_distinto', lambda email, excluir_id: True)

    with pytest.raises(ValueError) as excepcion:
        socios.crear_socio({'nombre': 'Juan', 'email': 'juan@example.com'})

    assert _codigos(excepcion) == ['socio.already.exists']
    assert _status(excepcion) == 409


def test_buscar_socio_por_id(monkeypatch):
    monkeypatch.setattr(db, 'obtener_socio_por_id', lambda socio_id: _socio_encontrado(socio_id))

    assert socios.buscar_socio_por_id(1)['id'] == 1


def test_actualizar_socio_parcial(monkeypatch):
    socio = _socio_encontrado(1)
    monkeypatch.setattr(db, 'obtener_socio_por_id', lambda socio_id: socio)
    monkeypatch.setattr(db, 'existe_socio_distinto', lambda email, excluir_id: False)
    monkeypatch.setattr(db, 'actualizar_socio_parcial', lambda socio_id, campos: socio.update(campos))

    resultado = socios.actualizar_socio_parcial(1, {'nombre': 'Nuevo'})

    assert resultado['nombre'] == 'Nuevo'


def test_actualizar_socio_parcial_email_duplicado(monkeypatch):
    monkeypatch.setattr(db, 'obtener_socio_por_id', lambda socio_id: _socio_encontrado(socio_id))
    monkeypatch.setattr(db, 'existe_socio_distinto', lambda email, excluir_id: True)

    with pytest.raises(ValueError) as excepcion:
        socios.actualizar_socio_parcial(1, {'email': 'otro@example.com'})

    assert _codigos(excepcion) == ['socio.already.exists']
    assert _status(excepcion) == 409


# --- reservas ---

def _reserva_encontrada(reserva_id=10, estado='confirmada'):
    return {
        'id': reserva_id,
        'id_socio': 1,
        'id_cancha': 2,
        'fecha_hora_inicio': '2026-08-17T10:00:00.000000-03:00',
        'fecha_hora_fin': '2026-08-17T12:00:00.000000-03:00',
        'estado': estado,
        'precio_hora': 1000,
        'precio_total': 2000
    }


def _cancha_activa():
    return {
        'id': 2,
        'nombre': 'Cancha A',
        'id_deporte': 1,
        'precio_hora': 1000,
        'techada': False,
        'activa': True
    }


def _socio_activo():
    return {'id': 1, 'nombre': 'Juan', 'email': 'juan@example.com', 'activo': True}


def test_listar_reservas(monkeypatch):
    monkeypatch.setattr(db, 'obtener_todas_las_reservas', lambda **kwargs: ([_reserva_encontrada()], 1))

    filas, total = reservas.listar_reservas({
        'id_cancha': None,
        'id_socio': None,
        'estado': None,
        'fecha_desde': None,
        'fecha_hasta': None,
        'offset': 0,
        'limit': 10
    })

    assert total == 1
    assert filas[0]['id'] == 10


def test_crear_reserva_ok(monkeypatch):
    monkeypatch.setattr(db, 'obtener_socio_por_id', lambda socio_id: _socio_activo())
    monkeypatch.setattr(db, 'obtener_cancha_por_id', lambda cancha_id: _cancha_activa())
    monkeypatch.setattr(db, 'existe_reserva_superpuesta', lambda *args, **kwargs: False)

    llamadas = []
    monkeypatch.setattr(db, 'insertar_reserva', lambda *args: llamadas.append(args) or 10)
    monkeypatch.setattr(db, 'obtener_reserva_por_id', lambda reserva_id: _reserva_encontrada(reserva_id))

    resultado = reservas.crear_reserva({
        'id_socio': 1,
        'id_cancha': 2,
        'fecha_hora_inicio': '2026-08-17T10:00:00.000000-03:00',
        'fecha_hora_fin': '2026-08-17T12:00:00.000000-03:00'
    })

    assert resultado['id'] == 10
    assert resultado['precio_total'] == 2000
    assert len(llamadas) == 1
    assert llamadas[0][4] == 'confirmada'


def test_crear_reserva_socio_inactivo(monkeypatch):
    socio = dict(_socio_activo())
    socio['activo'] = False
    monkeypatch.setattr(db, 'obtener_socio_por_id', lambda socio_id: socio)

    with pytest.raises(ValueError) as excepcion:
        reservas.crear_reserva({
            'id_socio': 1,
            'id_cancha': 2,
            'fecha_hora_inicio': '2026-08-17T10:00:00.000000-03:00',
            'fecha_hora_fin': '2026-08-17T12:00:00.000000-03:00'
        })

    assert _codigos(excepcion) == ['socio.not.active']
    assert _status(excepcion) == 400


def test_crear_reserva_cancha_inactiva(monkeypatch):
    monkeypatch.setattr(db, 'obtener_socio_por_id', lambda socio_id: _socio_activo())
    cancha = dict(_cancha_activa())
    cancha['activa'] = False
    monkeypatch.setattr(db, 'obtener_cancha_por_id', lambda cancha_id: cancha)

    with pytest.raises(ValueError) as excepcion:
        reservas.crear_reserva({
            'id_socio': 1,
            'id_cancha': 2,
            'fecha_hora_inicio': '2026-08-17T10:00:00.000000-03:00',
            'fecha_hora_fin': '2026-08-17T12:00:00.000000-03:00'
        })

    assert _codigos(excepcion) == ['cancha.not.active']
    assert _status(excepcion) == 400


def test_crear_reserva_conflict(monkeypatch):
    monkeypatch.setattr(db, 'obtener_socio_por_id', lambda socio_id: _socio_activo())
    monkeypatch.setattr(db, 'obtener_cancha_por_id', lambda cancha_id: _cancha_activa())
    monkeypatch.setattr(db, 'existe_reserva_superpuesta', lambda *args, **kwargs: True)

    with pytest.raises(ValueError) as excepcion:
        reservas.crear_reserva({
            'id_socio': 1,
            'id_cancha': 2,
            'fecha_hora_inicio': '2026-08-17T10:00:00.000000-03:00',
            'fecha_hora_fin': '2026-08-17T12:00:00.000000-03:00'
        })

    assert _codigos(excepcion) == ['reserva.conflict']
    assert _status(excepcion) == 409


def test_cambiar_estado_reserva_cancelar_ok(monkeypatch):
    inicio = dt.datetime(2026, 8, 10, 10, 0, 0)
    fin = dt.datetime(2026, 8, 10, 12, 0, 0)

    reserva = {
        'id': 10,
        'id_socio': 1,
        'id_cancha': 2,
        'fecha_hora_inicio': inicio,
        'fecha_hora_fin': fin,
        'estado': 'confirmada',
        'precio_hora': 1000,
        'precio_total': 2000
    }

    monkeypatch.setattr(reservas, 'datetime', _DatetimeFijo(dt.datetime(2026, 8, 1, 0, 0, 0)))
    monkeypatch.setattr(db, 'obtener_reserva_por_id', lambda reserva_id: reserva)
    monkeypatch.setattr(db, 'actualizar_estado_reserva', lambda reserva_id, estado: reserva.update({'estado': estado}))

    resultado = reservas.cambiar_estado_reserva(10, {'estado': 'cancelada'})

    assert resultado['estado'] == 'cancelada'


def test_cambiar_estado_reserva_finalizar_ok(monkeypatch):
    inicio = dt.datetime(2026, 8, 1, 10, 0, 0)
    fin = dt.datetime(2026, 8, 1, 12, 0, 0)

    reserva = {
        'id': 10,
        'id_socio': 1,
        'id_cancha': 2,
        'fecha_hora_inicio': inicio,
        'fecha_hora_fin': fin,
        'estado': 'confirmada',
        'precio_hora': 1000,
        'precio_total': 2000
    }

    monkeypatch.setattr(reservas, 'datetime', _DatetimeFijo(dt.datetime(2026, 8, 2, 0, 0, 0)))
    monkeypatch.setattr(db, 'obtener_reserva_por_id', lambda reserva_id: reserva)
    monkeypatch.setattr(db, 'actualizar_estado_reserva', lambda reserva_id, estado: reserva.update({'estado': estado}))

    resultado = reservas.cambiar_estado_reserva(10, {'estado': 'finalizada'})

    assert resultado['estado'] == 'finalizada'


def test_cambiar_estado_reserva_transicion_invalida(monkeypatch):
    inicio = dt.datetime(2026, 8, 10, 10, 0, 0)
    fin = dt.datetime(2026, 8, 10, 12, 0, 0)

    monkeypatch.setattr(reservas, 'datetime', _DatetimeFijo(dt.datetime(2026, 8, 1, 0, 0, 0)))
    monkeypatch.setattr(db, 'obtener_reserva_por_id', lambda reserva_id: {
        'id': reserva_id,
        'id_socio': 1,
        'id_cancha': 2,
        'fecha_hora_inicio': inicio,
        'fecha_hora_fin': fin,
        'estado': 'finalizada',
        'precio_hora': 1000,
        'precio_total': 2000
    })

    with pytest.raises(ValueError) as excepcion:
        reservas.cambiar_estado_reserva(10, {'estado': 'cancelada'})

    assert _codigos(excepcion) == ['reserva.estado.transicion.invalida']
