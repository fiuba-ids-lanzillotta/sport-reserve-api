# sport-reserve-api

API de reservas de canchas de club deportivo construida con Flask.

Esta rama (`main`) contiene la versión base con persistencia en archivos CSV (sin MySQL y sin extensiones opcionales).

## 📋 Requerimientos de Software

- **Python 3.7+** instalado y agregado al PATH ([descargar](https://www.python.org/downloads/))
- Conexión a internet para descargar dependencias

##  Instalación y Ejecución

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

## 🗂️ Persistencia

La información se almacena en archivos CSV dentro de la carpeta `data/`:

- `data/deportes.csv`
- `data/canchas.csv`
- `data/socios.csv`
- `data/reservas.csv`

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

## 📦 Dependencias

- **Flask 2.3.2** - Framework web
- **Werkzeug 2.3.6** - Utilidades WSGI
- **requests 2.31.0** - Solicitudes HTTP

## 📝 Estructura del Proyecto

```
sport-reserve-api/
├── app.py
├── requirements.txt
├── setup_virtualenv.sh
├── setup_virtualenv.bat
├── setup_pipenv.sh
├── setup_pipenv.bat
├── data/
│   ├── deportes.csv
│   ├── canchas.csv
│   ├── socios.csv
│   └── reservas.csv
├── sport_reserve/
│   ├── constants.py
│   ├── db.py
│   ├── pagination.py
│   ├── utils.py
│   ├── routes/
│   │   ├── deportes.py
│   │   ├── canchas.py
│   │   ├── socios.py
│   │   └── reservas.py
│   ├── services/
│   │   ├── deportes.py
│   │   ├── canchas.py
│   │   ├── socios.py
│   │   └── reservas.py
│   └── validators/
│       ├── canchas.py
│       ├── socios.py
│       └── reservas.py
├── docs/
│   ├── swagger.yaml
│   └── enunciado.md
├── README.md
└── LICENSE
```

## 📄 Licencia

Consulta el archivo [LICENSE](LICENSE) para más información.
