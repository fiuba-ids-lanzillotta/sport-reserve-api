FORMATO_FECHA = '%Y-%m-%d'
FORMATO_HORA = '%H:%M:%S'

# Patrón exigido por el contrato para los timestamps de reservas:
# YYYY-MM-DDTHH:MM:SS.ffffff-03:00
PATRON_FECHA_HORA = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}-03:00$'
SUFIJO_ZONA_HORARIA = '-03:00'

ESTADOS_RESERVA = {'confirmada', 'cancelada', 'finalizada'}

MIN_OFFSET = 0
MIN_LIMIT = 1
MAX_LIMIT = 100
MIN_ID = 1
MIN_PRECIO_HORA = 1

DEFAULT_OFFSET = '0'
DEFAULT_LIMIT = '10'

# URL base de la API
BASE_URL = '/sport_reserve_api'

# Rutas de archivos CSV para la persistencia en la rama main
RUTA_DATOS = 'data'
ARCHIVO_DEPORTES  = f'{RUTA_DATOS}/deportes.csv'
ARCHIVO_CANCHAS   = f'{RUTA_DATOS}/canchas.csv'
ARCHIVO_SOCIOS    = f'{RUTA_DATOS}/socios.csv'
ARCHIVO_RESERVAS  = f'{RUTA_DATOS}/reservas.csv'

# Códigos de error
ERROR_CODE_INVALID_BODY = 'invalid.body'
ERROR_CODE_INVALID_MIN_VALUE = 'invalid.min.value'
ERROR_CODE_INVALID_MAX_VALUE = 'invalid.max.value'

ERROR_CODE_DEPORTE_NOT_FOUND = 'deporte.not.found'

ERROR_CODE_CANCHA_NOT_FOUND = 'cancha.not.found'
ERROR_CODE_CANCHA_NOT_ACTIVE = 'cancha.not.active'
ERROR_CODE_CANCHA_HAS_RESERVAS = 'cancha.has.reservas'
ERROR_CODE_CANCHA_DISPONIBILIDAD_CONFLICT = 'cancha.disponibilidad.conflict'

ERROR_CODE_SOCIO_NOT_FOUND = 'socio.not.found'
ERROR_CODE_SOCIO_NOT_ACTIVE = 'socio.not.active'
ERROR_CODE_SOCIO_EXISTS = 'socio.already.exists'

ERROR_CODE_RESERVA_NOT_FOUND = 'reserva.not.found'
ERROR_CODE_RESERVA_CONFLICT = 'reserva.conflict'
ERROR_CODE_RESERVA_ESTADO_INVALIDO = 'reserva.estado.invalido'
ERROR_CODE_RESERVA_ESTADO_TRANSICION = 'reserva.estado.transicion.invalida'
ERROR_CODE_RESERVA_ESTADO_TEMPORAL = 'reserva.estado.temporal.invalido'
