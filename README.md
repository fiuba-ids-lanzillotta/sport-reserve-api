# sport-reserve-api

API de reservas de canchas de club deportivo construida con Flask.

## 📋 Requerimientos de Software

### Linux / macOS
- Sistema operativo Unix-based
- **MySQL 8+** instalado y en ejecución
- Conexión a internet para descargar dependencias

### Windows
- **Python 3.7+** instalado y agregado al PATH ([descargar](https://www.python.org/downloads/))
- **MySQL 8+** instalado y en ejecución ([descargar](https://dev.mysql.com/downloads/mysql/))
- Conexión a internet para descargar dependencias

## 🗄️ Base de Datos

La aplicación requiere una base de datos MySQL activa. Antes de levantar la aplicación, ejecutar los scripts SQL en el siguiente orden:

### 1. Crear el esquema (DDL)

```bash
mysql -u root -p < db/ddl.sql
```

### 2. Cargar los datos iniciales (DML)

```bash
mysql -u root -p < db/dml.sql
```

### Levantar MySQL con Docker Compose

Como alternativa, puedes levantar una base de datos MySQL con los scripts de inicialización automáticos:

```bash
docker-compose up -d
```

Esto hará lo siguiente:

- Descargará la imagen `mysql:8` si no está disponible localmente.
- Creará la base de datos `sport_reserve`.
- Ejecutará `db/ddl.sql` para crear el esquema.
- Ejecutará `db/dml.sql` para popular las tablas con datos iniciales.
- Publicará el puerto `3306` para que la API pueda conectarse desde `localhost`.

La base de datos conservará sus datos entre reinicios gracias al volumen `mysql_data`.

Para detenerla:

```bash
docker-compose down
```

Para detenerla y eliminar los datos persistentes:

```bash
docker-compose down -v
```

### Configuración de conexión

Por defecto la aplicación se conecta a una instancia local de MySQL:

| Parámetro    | Valor por defecto |
|--------------|-------------------|
| Host         | `localhost`       |
| Puerto       | `3306`            |
| Usuario      | `root`            |
| Contraseña   | *(vacía)*        |
| Base de datos| `sport_reserve`   |

Para cambiar la configuración, editar las constantes en `sport_reserve/constants.py`.

## 🚀 Instalación y Ejecución

### Linux / macOS

#### Opción 1: Usar virtualenv (Recomendado)

```bash
./setup_virtualenv.sh
```

#### Opción 2: Usar pipenv

```bash
./setup_pipenv.sh
```

### Windows

#### Opción 1: Usar virtualenv (Recomendado)

```bat
setup_virtualenv.bat
```

#### Opción 2: Usar pipenv

```bat
setup_pipenv.bat
```

## 🔧 Ejecución Manual

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Windows

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## 🧪 Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## 🌐 Acceso a la API

Una vez ejecutada la aplicación:

- **API base**: `http://localhost:5000/sport_reserve_api`

## 🔗 Endpoints

### Deportes

| Método | URL | Descripción |
|--------|-----|-------------|
| GET    | `/sport_reserve_api/deportes` | Listar deportes precargados |

### Canchas

| Método | URL | Descripción |
|--------|-----|-------------|
| GET    | `/sport_reserve_api/canchas` | Listar canchas con filtros y paginación |
| POST   | `/sport_reserve_api/canchas` | Crear una cancha |
| GET    | `/sport_reserve_api/canchas/{id}` | Obtener una cancha por ID |
| PATCH  | `/sport_reserve_api/canchas/{id}` | Actualizar parcialmente una cancha |
| DELETE | `/sport_reserve_api/canchas/{id}` | Eliminar una cancha |
| GET    | `/sport_reserve_api/canchas/disponibles` | Consultar canchas disponibles en un intervalo |

### Socios

| Método | URL | Descripción |
|--------|-----|-------------|
| GET    | `/sport_reserve_api/socios` | Listar socios con filtros y paginación |
| POST   | `/sport_reserve_api/socios` | Crear un socio |
| GET    | `/sport_reserve_api/socios/{id}` | Obtener un socio por ID |
| PATCH  | `/sport_reserve_api/socios/{id}` | Actualizar parcialmente un socio |

### Reservas

| Método | URL | Descripción |
|--------|-----|-------------|
| GET    | `/sport_reserve_api/reservas` | Listar reservas con filtros y paginación |
| POST   | `/sport_reserve_api/reservas` | Crear una reserva |
| GET    | `/sport_reserve_api/reservas/{id}` | Obtener una reserva por ID |
| PUT    | `/sport_reserve_api/reservas/{id}/estado` | Cambiar el estado de una reserva |

### Extensiones

| Método | URL | Descripción |
|--------|-----|-------------|
| GET    | `/sport_reserve_api/bloqueos` | Listar bloqueos de mantenimiento |
| POST   | `/sport_reserve_api/bloqueos` | Crear un bloqueo |
| DELETE | `/sport_reserve_api/bloqueos/{id}` | Eliminar un bloqueo |
| POST   | `/sport_reserve_api/reservas/recurrentes` | Crear reservas recurrentes |

## 📦 Dependencias

- **Flask 2.3.2** - Framework web
- **Werkzeug 2.3.6** - Utilidades WSGI
- **requests 2.31.0** - Solicitudes HTTP
- **SQLAlchemy 2.0.36** - Toolkit SQL (queries raw)
- **PyMySQL 1.1.1** - Driver MySQL

## 📝 Estructura del Proyecto

```
sport-reserve-api/
├── app.py
├── requirements.txt
├── setup_virtualenv.sh
├── setup_virtualenv.bat
├── setup_pipenv.sh
├── setup_pipenv.bat
├── db/
│   ├── ddl.sql
│   └── dml.sql
├── sport_reserve/
│   ├── constants.py
│   ├── db.py
│   ├── pagination.py
│   ├── utils.py
│   ├── routes/
│   │   ├── deportes.py
│   │   ├── canchas.py
│   │   ├── socios.py
│   │   ├── reservas.py
│   │   ├── bloqueos.py
│   │   └── recurrentes.py
│   ├── services/
│   │   ├── deportes.py
│   │   ├── canchas.py
│   │   ├── socios.py
│   │   ├── reservas.py
│   │   ├── bloqueos.py
│   │   └── recurrentes.py
│   └── validators/
│       ├── canchas.py
│       ├── socios.py
│       ├── reservas.py
│       ├── bloqueos.py
│       └── recurrentes.py
├── docs/
│   ├── swagger.yaml
│   └── enunciado.md
├── README.md
└── LICENSE
```

## 📄 Licencia

Consulta el archivo [LICENSE](LICENSE) para más información.
