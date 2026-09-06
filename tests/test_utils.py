import pytest
from datetime import datetime, time

from sport_reserve.constants import FORMATO_FECHA, FORMATO_HORA, SUFIJO_ZONA_HORARIA
from sport_reserve.utils import (
    construir_error_api,
    validar_entero,
    validar_minimo,
    validar_maximo,
    validar_booleano,
    validar_enum,
    validar_estado_reserva,
    validar_formato_fecha,
    validar_formato_hora,
    parsear_fecha_hora,
    formatear_fecha_hora,
    validar_params_paginacion,
    validar_id,
)


def _codigos(excepcion):
    """Extrae los cÔö£Ôöédigos de error de un ValueError de la API."""
    return [error['code'] for error in excepcion.value.args[0]['errors']]


# --- construir_error_api ---

def test_construir_error_api():
    payload = construir_error_api(
        code='test.code',
        message='Mensaje',
        description='DescripciÔö£Ôöén',
        level='warning'
    )

    assert payload == {
        'errors': [{
            'code': 'test.code',
            'message': 'Mensaje',
            'level': 'warning',
            'description': 'DescripciÔö£Ôöén'
        }]
    }


# --- validar_entero ---

def test_validar_entero_ok():
    assert validar_entero('42', 'id') == 42
    assert validar_entero('12a3', 'id') == 123


@pytest.mark.parametrize('valor', ['abc', '3.5', ''])
def test_validar_entero_invalido(valor):
    with pytest.raises(ValueError) as excepcion:
        validar_entero(valor, 'id')

    assert _codigos(excepcion) == ['invalid.id.format']


# --- min / max ---

def test_validar_minimo():
    assert validar_minimo(5, 1, 'n') == 5

    with pytest.raises(ValueError) as excepcion:
        validar_minimo(0, 1, 'n')

    assert _codigos(excepcion) == ['invalid.min.value']


def test_validar_maximo():
    assert validar_maximo(5, 10, 'n') == 5

    with pytest.raises(ValueError) as excepcion:
        validar_maximo(11, 10, 'n')

    assert _codigos(excepcion) == ['invalid.max.value']


# --- booleano ---

@pytest.mark.parametrize('valor,esperado', [
    (True, True),
    (False, False),
    ('true', True),
    ('False', False),
])
def test_validar_booleano_ok(valor, esperado):
    assert validar_booleano(valor, 'activo') is esperado


@pytest.mark.parametrize('valor', ['si', '2', 0])
def test_validar_booleano_invalido(valor):
    with pytest.raises(ValueError) as excepcion:
        validar_booleano(valor, 'activo')

    assert _codigos(excepcion) == ['invalid.activo.format']


# --- enum ---

def test_validar_enum_ok():
    assert validar_enum('Activo', {'activo', 'inactivo'}, 'estado') == 'activo'


def test_validar_enum_invalido():
    with pytest.raises(ValueError) as excepcion:
        validar_enum('otro', {'activo', 'inactivo'}, 'estado')

    assert _codigos(excepcion) == ['invalid.estado']


def test_validar_estado_reserva_ok():
    assert validar_estado_reserva('Confirmada') == 'confirmada'


def test_validar_estado_reserva_invalido():
    with pytest.raises(ValueError) as excepcion:
        validar_estado_reserva('xyz')

    assert _codigos(excepcion) == ['invalid.estado']


# --- fechas y horas ---

def test_validar_formato_fecha_ok():
    resultado = validar_formato_fecha('2026-08-17', FORMATO_FECHA, 'fecha')
    assert resultado == datetime(2026, 8, 17)


@pytest.mark.parametrize('valor', ['17/08/2026', '2026-13-01', 'no-fecha', ''])
def test_validar_formato_fecha_invalida(valor):
    with pytest.raises(ValueError) as excepcion:
        validar_formato_fecha(valor, FORMATO_FECHA, 'fecha')

    assert _codigos(excepcion) == ['invalid.fecha.format']


def test_validar_formato_hora_ok():
    resultado = validar_formato_hora('14:30:00', 'hora')
    assert resultado == time(14, 30, 0)


@pytest.mark.parametrize('valor', ['14:30', 'no-hora', ''])
def test_validar_formato_hora_invalida(valor):
    with pytest.raises(ValueError) as excepcion:
        validar_formato_hora(valor, 'hora')

    assert _codigos(excepcion) == ['invalid.hora.format']


def test_parsear_fecha_hora_ok():
    cadena = '2026-08-17T14:30:00.000000-03:00'
    resultado = parsear_fecha_hora(cadena, 'fecha_hora')

    assert resultado == datetime(2026, 8, 17, 14, 30, 0)
    assert resultado.tzinfo is None


@pytest.mark.parametrize('valor', [
    '2026-08-17 14:30:00',
    'no-fecha',
    '',
    '2026-08-17T14:30:00-03:00'
])
def test_parsear_fecha_hora_invalida(valor):
    with pytest.raises(ValueError) as excepcion:
        parsear_fecha_hora(valor, 'fecha_hora')

    assert _codigos(excepcion) == ['invalid.fecha_hora.format']


def test_formatear_fecha_hora_con_datetime():
    dt = datetime(2026, 8, 17, 14, 30, 0, 0)
    assert formatear_fecha_hora(dt) == '2026-08-17T14:30:00.000000-03:00'


def test_formatear_fecha_hora_con_string():
    cadena = '2026-08-17T14:30:00.000000-03:00'
    assert formatear_fecha_hora(cadena) == cadena


# --- paginaciÔö£Ôöén ---

def test_validar_params_paginacion_defaults():
    assert validar_params_paginacion({}) == {'offset': 0, 'limit': 10}


def test_validar_params_paginacion_ok():
    assert validar_params_paginacion({'_offset': '20', '_limit': '5'}) == {'offset': 20, 'limit': 5}


def test_validar_params_paginacion_limit_minimo():
    with pytest.raises(ValueError) as excepcion:
        validar_params_paginacion({'_limit': '0'})

    assert _codigos(excepcion) == ['invalid.min.value']


def test_validar_params_paginacion_limit_maximo():
    with pytest.raises(ValueError) as excepcion:
        validar_params_paginacion({'_limit': '101'})

    assert _codigos(excepcion) == ['invalid.max.value']


def test_validar_params_paginacion_offset_invalido():
    with pytest.raises(ValueError) as excepcion:
        validar_params_paginacion({'_offset': 'x'})

    assert _codigos(excepcion) == ['invalid._offset.format']


# --- ids ---

def test_validar_id_ok():
    assert validar_id('5') == 5


def test_validar_id_minimo():
    with pytest.raises(ValueError) as excepcion:
        validar_id('0')

    assert _codigos(excepcion) == ['invalid.min.value']


def test_validar_id_formato_invalido():
    with pytest.raises(ValueError) as excepcion:
        validar_id('abc')

    assert _codigos(excepcion) == ['invalid.id.format']
