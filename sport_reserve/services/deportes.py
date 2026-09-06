from .. import db


def construir_deporte_dto(deporte: dict) -> dict:
    return {
        'id': deporte['id'],
        'nombre': deporte['nombre']
    }


def listar_deportes() -> list[dict]:
    deportes = db.obtener_todos_los_deportes()
    return [construir_deporte_dto(d) for d in deportes]
