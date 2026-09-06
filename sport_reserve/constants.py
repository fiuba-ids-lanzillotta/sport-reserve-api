import os

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
MIN_CANTIDAD_SEMANAS = 2
MAX_CANTIDAD_SEMANAS = 12
DEFAULT_OFFSET = '0'
DEFAULT_LIMIT = '10'

# URL base de la API
BASE_URL = '/sport_reserve_api'

# Configuración de la base de datos (conexión local por defecto)
# Se puede sobreescribir mediante variables de entorno para Docker Compose.
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', 3306))
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_NAME = os.environ.get('DB_NAME', 'sport_reserve')
DB_URL = os.environ.get(
    'DB_URL',
    f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)

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

ERROR_CODE_BLOQUEO_NOT_FOUND = 'bloqueo.not.found'
ERROR_CODE_BLOQUEO_CONFLICT = 'bloqueo.conflict'
