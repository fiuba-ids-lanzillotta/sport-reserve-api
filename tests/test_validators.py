import pytest

from sport_reserve.validators.canchas import (
    validar_params_canchas,
    validar_params_disponibles,
    validar_body_cancha,
    validar_body_cancha_patch,
)
from sport_reserve.validators.socios import (
    validar_params_socios,
    validar_body_socio,
    validar_body_socio_patch,
)
from sport_reserve.validators.reservas import (
    validar_params_reservas,
    validar_body_reserva,
    validar_body_estado_reserva,
)


def _codigos(excepcion):
    """Extrae los códigos de error de un ValueError de la API."""
    return [error['code'] for error in excepcion.value.args[0]['errors']]


# --- canchas: params ---

def test_validar_params_canchas_default():
    params = validar_params_canchas({})

    assert params['offset'] == 0
    assert params['limit'] == 10
    assert params['id_deporte'] is None
    assert params['nombre'] is None
    assert params['techada'] is None
    assert params['activa'] is None


def test_validar_params_canchas_con_filtros():
    params = validar_params_canchas({
        'id_deporte': '1',
        'nombre': 'futbol',
        'techada': 'true',
        'activa': 'false',
        '_offset': '5',
        '_limit': '20'
    })

    assert params['id_deporte'] == 1
    assert params['nombre'] == 'futbol'
    assert params['techada'] is True
    assert params['activa'] is False
    assert params['offset'] == 5
    assert params['limit'] == 20


def test_validar_params_canchas_id_deporte_invalido():
    with pytest.raises(ValueError) as excepcion:
        validar_params_canchas({'id_deporte': '0'})

    assert 'invalid.min.value' in _codigos(excepcion)


def test_validar_params_canchas_booleano_invalido():
    with pytest.raises(ValueError) as excepcion:
        validar_params_canchas({'techada': 'si'})

    assert 'invalid.techada.format' in _codigos(excepcion)


# --- canchas: disponibles ---

def test_validar_params_disponibles_ok():
    params = validar_params_disponibles({
        'fecha': '2026-08-17',
        'hora_inicio': '10:00:00',
        'hora_fin': '12:00:00',
        'id_deporte': '1',
        'techada': 'true'
    })

    assert params['fecha'] == '2026-08-17'
    assert params['hora_inicio'] == '10:00:00'
    assert params['hora_fin'] == '12:00:00'
    assert params['id_deporte'] == 1
    assert params['techada'] is True


def test_validar_params_disponibles_fecha_requerida():
    with pytest.raises(ValueError) as excepcion:
        validar_params_disponibles({})

    assert 'required.fecha' in _codigos(excepcion)


def test_validar_params_disponibles_horas_invalidas():
    with pytest.raises(ValueError) as excepcion:
        validar_params_disponibles({
            'fecha': '2026-08-17',
            'hora_inicio': '12:00:00',
            'hora_fin': '10:00:00'
        })

    assert 'invalid.hora_fin' in _codigos(excepcion)


# --- canchas: body ---

def test_validar_body_cancha_ok():
    datos = validar_body_cancha({
        'nombre': 'Cancha A',
        'id_deporte': 1,
        'precio_hora': 1000
    })

    assert datos == {
        'nombre': 'Cancha A',
        'id_deporte': 1,
        'precio_hora': 1000,
        'techada': False,
        'activa': True
    }


def test_validar_body_cancha_campos_requeridos():
    with pytest.raises(ValueError) as excepcion:
        validar_body_cancha({})

    assert set(_codigos(excepcion)) == {'required.nombre', 'required.id_deporte', 'required.precio_hora'}


def test_validar_body_cancha_valores_invalidos():
    with pytest.raises(ValueError) as excepcion:
        validar_body_cancha({
            'nombre': 'Cancha A',
            'id_deporte': 0,
            'precio_hora': 0,
            'techada': 'si'
        })

    assert 'invalid.min.value' in _codigos(excepcion)
    assert 'invalid.techada.format' in _codigos(excepcion)


# --- canchas: patch ---

def test_validar_body_cancha_patch_ok():
    assert validar_body_cancha_patch({'nombre': 'Nuevo'}) == {'nombre': 'Nuevo'}
    assert validar_body_cancha_patch({'precio_hora': 500}) == {'precio_hora': 500}
    assert validar_body_cancha_patch({'techada': False}) == {'techada': False}


def test_validar_body_cancha_patch_vacio():
    with pytest.raises(ValueError) as excepcion:
        validar_body_cancha_patch({})

    assert _codigos(excepcion) == ['invalid.body']


# --- socios: params ---

def test_validar_params_socios_default():
    params = validar_params_socios({})

    assert params['offset'] == 0
    assert params['limit'] == 10
    assert params['nombre'] is None
    assert params['activo'] is None


def test_validar_params_socios_con_filtros():
    params = validar_params_socios({
        'nombre': 'juan',
        'activo': 'true',
        '_offset': '0',
        '_limit': '5'
    })

    assert params['nombre'] == 'juan'
    assert params['activo'] is True
    assert params['limit'] == 5


# --- socios: body ---

def test_validar_body_socio_ok():
    datos = validar_body_socio({'nombre': 'Juan Pérez', 'email': 'juan@example.com'})

    assert datos == {'nombre': 'Juan Pérez', 'email': 'juan@example.com'}


def test_validar_body_socio_campos_requeridos():
    with pytest.raises(ValueError) as excepcion:
        validar_body_socio({})

    assert set(_codigos(excepcion)) == {'required.nombre', 'required.email'}


def test_validar_body_socio_formatos_invalidos():
    with pytest.raises(ValueError) as excepcion:
        validar_body_socio({'nombre': 'Juan123', 'email': 'no-es-mail'})

    assert 'invalid.nombre.format' in _codigos(excepcion)
    assert 'invalid.email.format' in _codigos(excepcion)


# --- socios: patch ---

def test_validar_body_socio_patch_ok():
    assert validar_body_socio_patch({'nombre': 'Nuevo'}) == {'nombre': 'Nuevo'}
    assert validar_body_socio_patch({'email': 'nuevo@example.com'}) == {'email': 'nuevo@example.com'}


def test_validar_body_socio_patch_vacio():
    with pytest.raises(ValueError) as excepcion:
        validar_body_socio_patch({})

    assert _codigos(excepcion) == ['invalid.body']


# --- reservas: params ---

def test_validar_params_reservas_default():
    params = validar_params_reservas({})

    assert params['offset'] == 0
    assert params['limit'] == 10
    assert params['id_cancha'] is None
    assert params['estado'] is None


def test_validar_params_reservas_con_filtros():
    params = validar_params_reservas({
        'id_cancha': '2',
        'id_socio': '3',
        'estado': 'confirmada',
        'fecha_desde': '2026-08-01',
        'fecha_hasta': '2026-08-31'
    })

    assert params['id_cancha'] == 2
    assert params['id_socio'] == 3
    assert params['estado'] == 'confirmada'
    assert params['fecha_desde'] == '2026-08-01'
    assert params['fecha_hasta'] == '2026-08-31'


def test_validar_params_reservas_rango_invalido():
    with pytest.raises(ValueError) as excepcion:
        validar_params_reservas({
            'fecha_desde': '2026-08-31',
            'fecha_hasta': '2026-08-01'
        })

    assert _codigos(excepcion) == ['invalid.fecha_rango']


# --- reservas: body ---

def test_validar_body_reserva_ok():
    datos = validar_body_reserva({
        'id_socio': 1,
        'id_cancha': 2,
        'fecha_hora_inicio': '2026-08-17T10:00:00.000000-03:00',
        'fecha_hora_fin': '2026-08-17T12:00:00.000000-03:00'
    })

    assert datos['id_socio'] == 1
    assert datos['id_cancha'] == 2
    assert datos['fecha_hora_inicio'] < datos['fecha_hora_fin']


def test_validar_body_reserva_campos_requeridos():
    with pytest.raises(ValueError) as excepcion:
        validar_body_reserva({})

    assert set(_codigos(excepcion)) == {
        'required.id_socio',
        'required.id_cancha',
        'required.fecha_hora_inicio',
        'required.fecha_hora_fin'
    }


def test_validar_body_reserva_fin_anterior():
    with pytest.raises(ValueError) as excepcion:
        validar_body_reserva({
            'id_socio': 1,
            'id_cancha': 2,
            'fecha_hora_inicio': '2026-08-17T12:00:00.000000-03:00',
            'fecha_hora_fin': '2026-08-17T10:00:00.000000-03:00'
        })

    assert _codigos(excepcion) == ['invalid.fecha_hora_fin']


# --- reservas: estado ---

def test_validar_body_estado_reserva_ok():
    assert validar_body_estado_reserva({'estado': 'cancelada'}) == {'estado': 'cancelada'}


def test_validar_body_estado_reserva_requerido():
    with pytest.raises(ValueError) as excepcion:
        validar_body_estado_reserva({})

    assert _codigos(excepcion) == ['required.estado']


def test_validar_body_estado_reserva_invalido():
    with pytest.raises(ValueError) as excepcion:
        validar_body_estado_reserva({'estado': 'xyz'})

    assert _codigos(excepcion) == ['invalid.estado']
