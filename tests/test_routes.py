"""Tests end-to-end de las rutas con test_client; la capa de datos está mockeada."""
import datetime as dt
import pytest

from sport_reserve import db
from sport_reserve.constants import BASE_URL
from sport_reserve.services import reservas as reservas_service


class _DatetimeFijo:
    """Sustituto de la clase datetime para devolver un 'now' determinista."""

    def __init__(self, valor):
        self.valor = valor

    def now(self):
        return self.valor


def _cancha(cancha_id=1):
    return {
        'id': cancha_id,
        'nombre': 'Cancha A',
        'id_deporte': 1,
        'precio_hora': 1000,
        'techada': 0,
        'activa': 1
    }


def _socio(socio_id=1):
    return {'id': socio_id, 'nombre': 'Juan', 'email': 'juan@example.com', 'activo': 1}


def _reserva(reserva_id=10, estado='confirmada'):
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


def _bloqueo(bloqueo_id=5):
    return {
        'id': bloqueo_id,
        'id_cancha': 1,
        'fecha': '2026-08-17',
        'hora_inicio': '10:00:00',
        'hora_fin': '12:00:00',
        'motivo': 'Mantenimiento'
    }


# --- deportes ---

def test_get_deportes(client, monkeypatch):
    monkeypatch.setattr(db, 'obtener_todos_los_deportes', lambda: [
        {'id': 1, 'nombre': 'Fútbol'},
        {'id': 2, 'nombre': 'Básquet'}
    ])

    respuesta = client.get(f'{BASE_URL}/deportes')

    assert respuesta.status_code == 200
    assert respuesta.get_json()['deportes'][0]['nombre'] == 'Fútbol'


# --- canchas ---

def test_get_canchas(client, monkeypatch):
    monkeypatch.setattr(db, 'obtener_canchas', lambda **kwargs: ([_cancha()], 1))

    respuesta = client.get(f'{BASE_URL}/canchas')

    assert respuesta.status_code == 200
    assert respuesta.get_json()['canchas'][0]['id'] == 1


def test_post_cancha_ok(client, monkeypatch):
    monkeypatch.setattr(db, 'obtener_deporte_por_id', lambda id_deporte: {'id': 1, 'nombre': 'Fútbol'})
    monkeypatch.setattr(db, 'insertar_cancha', lambda *args: 5)
    monkeypatch.setattr(db, 'obtener_cancha_por_id', lambda cancha_id: _cancha(cancha_id))

    respuesta = client.post(f'{BASE_URL}/canchas', json={
        'nombre': 'Cancha A',
        'id_deporte': 1,
        'precio_hora': 1000
    })

    assert respuesta.status_code == 201
    assert respuesta.data == b''


def test_post_cancha_deporte_no_encontrado(client, monkeypatch):
    monkeypatch.setattr(db, 'obtener_deporte_por_id', lambda id_deporte: {})

    respuesta = client.post(f'{BASE_URL}/canchas', json={
        'nombre': 'Cancha A',
        'id_deporte': 99,
        'precio_hora': 1000
    })

    assert respuesta.status_code == 404
    assert respuesta.get_json()['errors'][0]['code'] == 'deporte.not.found'


def test_get_cancha_por_id(client, monkeypatch):
    monkeypatch.setattr(db, 'obtener_cancha_por_id', lambda cancha_id: _cancha(cancha_id))

    respuesta = client.get(f'{BASE_URL}/canchas/1')

    assert respuesta.status_code == 200
    assert respuesta.get_json()['id'] == 1


def test_get_cancha_por_id_no_encontrada(client, monkeypatch):
    monkeypatch.setattr(db, 'obtener_cancha_por_id', lambda cancha_id: {})

    respuesta = client.get(f'{BASE_URL}/canchas/99')

    assert respuesta.status_code == 404


def test_patch_cancha(client, monkeypatch):
    cancha = _cancha(1)
    monkeypatch.setattr(db, 'obtener_cancha_por_id', lambda cancha_id: cancha)
    monkeypatch.setattr(db, 'actualizar_cancha_parcial', lambda cancha_id, campos: cancha.update(campos))

    respuesta = client.patch(f'{BASE_URL}/canchas/1', json={'nombre': 'Cancha B'})

    assert respuesta.status_code == 204
    assert respuesta.data == b''


def test_delete_cancha(client, monkeypatch):
    monkeypatch.setattr(db, 'obtener_cancha_por_id', lambda cancha_id: _cancha(cancha_id))
    monkeypatch.setattr(db, 'contar_reservas_por_cancha', lambda cancha_id: 0)
    monkeypatch.setattr(db, 'eliminar_cancha', lambda cancha_id: True)

    respuesta = client.delete(f'{BASE_URL}/canchas/1')

    assert respuesta.status_code == 204
    assert respuesta.data == b''


def test_get_canchas_disponibles(client, monkeypatch):
    monkeypatch.setattr(db, 'obtener_canchas_disponibles', lambda **kwargs: ([_cancha()], 1))

    respuesta = client.get(
        f'{BASE_URL}/canchas/disponibles?fecha=2026-08-17&hora_inicio=10:00:00&hora_fin=12:00:00'
    )

    assert respuesta.status_code == 200
    assert respuesta.get_json()['canchas'][0]['id'] == 1


# --- socios ---

def test_get_socios(client, monkeypatch):
    monkeypatch.setattr(db, 'obtener_todos_los_socios', lambda **kwargs: ([_socio()], 1))

    respuesta = client.get(f'{BASE_URL}/socios')

    assert respuesta.status_code == 200
    assert respuesta.get_json()['socios'][0]['nombre'] == 'Juan'


def test_post_socio_ok(client, monkeypatch):
    monkeypatch.setattr(db, 'existe_socio_distinto', lambda email, excluir_id: False)
    monkeypatch.setattr(db, 'insertar_socio', lambda nombre, email: 3)
    monkeypatch.setattr(db, 'obtener_socio_por_id', lambda socio_id: _socio(socio_id))

    respuesta = client.post(f'{BASE_URL}/socios', json={
        'nombre': 'Juan',
        'email': 'juan@example.com'
    })

    assert respuesta.status_code == 201
    assert respuesta.data == b''


def test_post_socio_duplicado(client, monkeypatch):
    monkeypatch.setattr(db, 'existe_socio_distinto', lambda email, excluir_id: True)

    respuesta = client.post(f'{BASE_URL}/socios', json={
        'nombre': 'Juan',
        'email': 'juan@example.com'
    })

    assert respuesta.status_code == 409
    assert respuesta.get_json()['errors'][0]['code'] == 'socio.already.exists'


def test_get_socio_por_id(client, monkeypatch):
    monkeypatch.setattr(db, 'obtener_socio_por_id', lambda socio_id: _socio(socio_id))

    respuesta = client.get(f'{BASE_URL}/socios/1')

    assert respuesta.status_code == 200
    assert respuesta.get_json()['id'] == 1


def test_patch_socio(client, monkeypatch):
    socio = _socio(1)
    monkeypatch.setattr(db, 'obtener_socio_por_id', lambda socio_id: socio)
    monkeypatch.setattr(db, 'existe_socio_distinto', lambda email, excluir_id: False)
    monkeypatch.setattr(db, 'actualizar_socio_parcial', lambda socio_id, campos: socio.update(campos))

    respuesta = client.patch(f'{BASE_URL}/socios/1', json={'nombre': 'Nuevo'})

    assert respuesta.status_code == 204
    assert respuesta.data == b''


# --- reservas ---

def test_get_reservas(client, monkeypatch):
    monkeypatch.setattr(db, 'obtener_todas_las_reservas', lambda **kwargs: ([_reserva()], 1))

    respuesta = client.get(f'{BASE_URL}/reservas')

    assert respuesta.status_code == 200
    assert respuesta.get_json()['reservas'][0]['id'] == 10


def test_post_reserva_ok(client, monkeypatch):
    monkeypatch.setattr(db, 'obtener_socio_por_id', lambda socio_id: _socio(socio_id))
    monkeypatch.setattr(db, 'obtener_cancha_por_id', lambda cancha_id: _cancha(cancha_id))
    monkeypatch.setattr(db, 'existe_reserva_superpuesta', lambda *args, **kwargs: False)
    monkeypatch.setattr(db, 'existe_bloqueo_superpuesto_para_reserva', lambda *args, **kwargs: False)
    monkeypatch.setattr(db, 'insertar_reserva', lambda *args: 10)
    monkeypatch.setattr(db, 'obtener_reserva_por_id', lambda reserva_id: _reserva(reserva_id))

    respuesta = client.post(f'{BASE_URL}/reservas', json={
        'id_socio': 1,
        'id_cancha': 2,
        'fecha_hora_inicio': '2026-08-17T10:00:00.000000-03:00',
        'fecha_hora_fin': '2026-08-17T12:00:00.000000-03:00'
    })

    assert respuesta.status_code == 201
    assert respuesta.data == b''


def test_post_reserva_conflict(client, monkeypatch):
    monkeypatch.setattr(db, 'obtener_socio_por_id', lambda socio_id: _socio(socio_id))
    monkeypatch.setattr(db, 'obtener_cancha_por_id', lambda cancha_id: _cancha(cancha_id))
    monkeypatch.setattr(db, 'existe_reserva_superpuesta', lambda *args, **kwargs: True)
    monkeypatch.setattr(db, 'existe_bloqueo_superpuesto_para_reserva', lambda *args, **kwargs: False)

    respuesta = client.post(f'{BASE_URL}/reservas', json={
        'id_socio': 1,
        'id_cancha': 2,
        'fecha_hora_inicio': '2026-08-17T10:00:00.000000-03:00',
        'fecha_hora_fin': '2026-08-17T12:00:00.000000-03:00'
    })

    assert respuesta.status_code == 409
    assert respuesta.get_json()['errors'][0]['code'] == 'reserva.conflict'


def test_get_reserva_por_id(client, monkeypatch):
    monkeypatch.setattr(db, 'obtener_reserva_por_id', lambda reserva_id: _reserva(reserva_id))

    respuesta = client.get(f'{BASE_URL}/reservas/10')

    assert respuesta.status_code == 200
    assert respuesta.get_json()['id'] == 10


def test_put_estado_reserva_cancelar(client, monkeypatch):
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

    monkeypatch.setattr(reservas_service, 'datetime', _DatetimeFijo(dt.datetime(2026, 8, 1, 0, 0, 0)))
    monkeypatch.setattr(db, 'obtener_reserva_por_id', lambda reserva_id: reserva)
    monkeypatch.setattr(db, 'actualizar_estado_reserva', lambda reserva_id, estado: reserva.update({'estado': estado}))
    monkeypatch.setattr(db, 'existe_reserva_superpuesta', lambda *args, **kwargs: False)
    monkeypatch.setattr(db, 'existe_bloqueo_superpuesto_para_reserva', lambda *args, **kwargs: False)

    respuesta = client.put(f'{BASE_URL}/reservas/10/estado', json={'estado': 'cancelada'})

    assert respuesta.status_code == 204
    assert respuesta.data == b''


# --- bloqueos ---

def test_get_bloqueos(client, monkeypatch):
    monkeypatch.setattr(db, 'obtener_bloqueos', lambda **kwargs: ([_bloqueo()], 1))

    respuesta = client.get(f'{BASE_URL}/bloqueos')

    assert respuesta.status_code == 200
    assert respuesta.get_json()['bloqueos'][0]['motivo'] == 'Mantenimiento'


def test_post_bloqueo_ok(client, monkeypatch):
    monkeypatch.setattr(db, 'obtener_cancha_por_id', lambda cancha_id: _cancha(cancha_id))
    monkeypatch.setattr(db, 'existe_reserva_superpuesta', lambda *args, **kwargs: False)
    monkeypatch.setattr(db, 'existe_bloqueo_superpuesto', lambda *args, **kwargs: False)
    monkeypatch.setattr(db, 'insertar_bloqueo', lambda *args: 5)
    monkeypatch.setattr(db, 'obtener_bloqueo_por_id', lambda bloqueo_id: _bloqueo(bloqueo_id))

    respuesta = client.post(f'{BASE_URL}/bloqueos', json={
        'id_cancha': 1,
        'fecha': '2026-08-17',
        'hora_inicio': '10:00:00',
        'hora_fin': '12:00:00',
        'motivo': 'Mantenimiento'
    })

    assert respuesta.status_code == 201
    assert respuesta.data == b''


def test_delete_bloqueo(client, monkeypatch):
    monkeypatch.setattr(db, 'eliminar_bloqueo', lambda bloqueo_id: True)

    respuesta = client.delete(f'{BASE_URL}/bloqueos/5')

    assert respuesta.status_code == 204


# --- reservas recurrentes ---

def test_post_reservas_recurrentes(client, monkeypatch):
    monkeypatch.setattr(db, 'obtener_socio_por_id', lambda socio_id: _socio(socio_id))
    monkeypatch.setattr(db, 'obtener_cancha_por_id', lambda cancha_id: _cancha(cancha_id))
    monkeypatch.setattr(db, 'existe_reserva_superpuesta', lambda *args, **kwargs: False)
    monkeypatch.setattr(db, 'existe_bloqueo_superpuesto_para_reserva', lambda *args, **kwargs: False)
    monkeypatch.setattr(db, 'insertar_reservas_batch', lambda reservas: [10, 11])
    monkeypatch.setattr(db, 'obtener_reserva_por_id', lambda reserva_id: _reserva(reserva_id))

    respuesta = client.post(f'{BASE_URL}/reservas/recurrentes', json={
        'id_socio': 1,
        'id_cancha': 2,
        'fecha_hora_inicio': '2026-08-17T10:00:00.000000-03:00',
        'fecha_hora_fin': '2026-08-17T11:00:00.000000-03:00',
        'cantidad_semanas': 2
    })

    assert respuesta.status_code == 201
    assert respuesta.data == b''


# --- listados vacios ---

def test_get_deportes_vacio(client, monkeypatch):
    monkeypatch.setattr(db, 'obtener_todos_los_deportes', lambda: [])

    respuesta = client.get(f'{BASE_URL}/deportes')

    assert respuesta.status_code == 204
    assert respuesta.data == b''


def test_get_canchas_vacio(client, monkeypatch):
    monkeypatch.setattr(db, 'obtener_canchas', lambda **kwargs: ([], 0))

    respuesta = client.get(f'{BASE_URL}/canchas')

    assert respuesta.status_code == 204
    assert respuesta.data == b''


def test_get_canchas_disponibles_vacio(client, monkeypatch):
    monkeypatch.setattr(db, 'obtener_canchas_disponibles', lambda **kwargs: ([], 0))

    respuesta = client.get(
        f'{BASE_URL}/canchas/disponibles?fecha=2026-08-17&hora_inicio=10:00:00&hora_fin=12:00:00'
    )

    assert respuesta.status_code == 204
    assert respuesta.data == b''


def test_get_socios_vacio(client, monkeypatch):
    monkeypatch.setattr(db, 'obtener_todos_los_socios', lambda **kwargs: ([], 0))

    respuesta = client.get(f'{BASE_URL}/socios')

    assert respuesta.status_code == 204
    assert respuesta.data == b''


def test_get_reservas_vacio(client, monkeypatch):
    monkeypatch.setattr(db, 'obtener_todas_las_reservas', lambda **kwargs: ([], 0))

    respuesta = client.get(f'{BASE_URL}/reservas')

    assert respuesta.status_code == 204
    assert respuesta.data == b''


def test_get_bloqueos_vacio(client, monkeypatch):
    monkeypatch.setattr(db, 'obtener_bloqueos', lambda **kwargs: ([], 0))

    respuesta = client.get(f'{BASE_URL}/bloqueos')

    assert respuesta.status_code == 204
    assert respuesta.data == b''
