# Ejercicio Práctico - API de Reservas de Club Deportivo

**Fecha de entrega:** 13/04/2026  
**Modalidad:** Trabajo grupal (hasta 4 personas)  
**Entrega:** Link a repositorio GitHub público

---

## 1. Objetivo

Desarrollar una API backend que permita gestionar la reserva de canchas de un club deportivo.

La solución deberá permitir:

- Consultar los deportes precargados del club.
- Crear, consultar, modificar y eliminar canchas.
- Consultar la disponibilidad de canchas en un intervalo de tiempo.
- Crear, consultar y modificar socios del club.
- Crear, listar, consultar y cambiar el estado de reservas.
- Implementar paginación en los listados.

Esta rama contiene la implementación base, sin extensiones opcionales.

---

## 2. Consideraciones generales

- La API debe seguir principios REST.
- Se debe respetar el contrato definido en `docs/swagger.yaml`.
- Se deberá implementar paginación utilizando `_limit` y `_offset`.
- No es necesario implementar autenticación.

---

## 3. Modelo de datos

### Entidad: Deporte

| Campo  | Tipo   | Descripción          |
|--------|--------|----------------------|
| id     | int    | Identificador único  |
| nombre | string | Nombre del deporte   |

### Entidad: Cancha

| Campo       | Tipo    | Descripción                       |
|-------------|---------|-----------------------------------|
| id          | int     | Identificador único               |
| nombre      | string  | Nombre de la cancha               |
| id_deporte  | int     | FK → Deporte                      |
| precio_hora | int     | Tarifa vigente por hora (centavos)|
| techada     | boolean | Indica si es cubierta             |
| activa      | boolean | Indica si admite nuevas reservas  |

### Entidad: Socio

| Campo  | Tipo    | Descripción                    |
|--------|---------|--------------------------------|
| id     | int     | Identificador único            |
| nombre | string  | Nombre completo                |
| email  | string  | Correo electrónico único       |
| activo | boolean | Indica si puede reservar       |

### Entidad: Reserva

| Campo             | Tipo    | Descripción                              |
|-------------------|---------|------------------------------------------|
| id                | int     | Identificador único                      |
| id_socio          | int     | FK → Socio                               |
| id_cancha         | int     | FK → Cancha                              |
| fecha_hora_inicio | string  | Inicio del intervalo (ISO con -03:00)    |
| fecha_hora_fin    | string  | Fin del intervalo (ISO con -03:00)       |
| estado            | string  | confirmada / cancelada / finalizada      |
| precio_hora       | int     | Tarifa histórica (centavos)              |
| precio_total      | int     | Importe total calculado (centavos)       |

---

## 4. API a implementar

### Endpoints base

- `GET /deportes`
- `GET /canchas`, `POST /canchas`, `GET /canchas/{id}`, `PATCH /canchas/{id}`, `DELETE /canchas/{id}`
- `GET /canchas/disponibles`
- `GET /socios`, `POST /socios`, `GET /socios/{id}`, `PATCH /socios/{id}`
- `GET /reservas`, `POST /reservas`, `GET /reservas/{id}`, `PUT /reservas/{id}/estado`

---

## 5. Paginación

Se implementa con `_limit` y `_offset`. La respuesta incluye navegación HATEOAS:

- `_first`
- `_prev`
- `_next`
- `_last`

---

## 6. Requisitos técnicos

- Lenguaje: Python
- Framework: Flask
- Persistencia: MySQL (rama con base de datos) o CSV (rama base)
- Buenas prácticas: separación de capas, validación de datos, manejo de errores

---

## 7. Evaluación

Se evaluará:

- Correcta implementación de endpoints.
- Respeto del contrato API.
- Manejo de paginación.
- Modelado de datos.
- Claridad del código.
- Organización del repositorio.
