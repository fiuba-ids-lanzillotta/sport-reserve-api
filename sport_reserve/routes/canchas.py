from flask import Blueprint, jsonify, request
from ..constants import ERROR_CODE_INVALID_BODY
from ..utils import construir_error_api
from ..pagination import construir_respuesta_paginada
from ..validators.canchas import validar_params_canchas, validar_params_disponibles, validar_id_cancha
from ..services import canchas as canchas_service

canchas_bp = Blueprint('canchas', __name__)


@canchas_bp.route('/canchas', methods=['GET'])
def get_canchas():
    try:
        params = validar_params_canchas(request.args.to_dict())
    except ValueError as e:
        return jsonify(e.args[0]), 400

    canchas, total = canchas_service.listar_canchas(params)

    response = construir_respuesta_paginada(
        datos={'canchas': canchas},
        total=total,
        offset=params['offset'],
        limit=params['limit'],
        base_url=request.base_url,
        params=request.args.to_dict()
    )

    return jsonify(response)


@canchas_bp.route('/canchas', methods=['POST'])
def post_cancha():
    body = request.get_json(silent=True)

    if body is None:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Cuerpo de la solicitud inválido',
            description='El cuerpo debe ser un JSON válido con Content-Type application/json'
        )), 400

    try:
        cancha = canchas_service.crear_cancha(body)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status

    return jsonify(cancha), 201


@canchas_bp.route('/canchas/<id>', methods=['GET'])
def get_cancha_por_id(id):
    try:
        id_cancha = validar_id_cancha(id)
    except ValueError as e:
        return jsonify(e.args[0]), 400

    cancha = canchas_service.buscar_cancha_por_id(id_cancha)

    if not cancha:
        return jsonify(construir_error_api(
            code='cancha.not.found',
            message='Cancha no encontrada',
            description=f"No existe una cancha con id '{id_cancha}'"
        )), 404

    return jsonify(cancha)


@canchas_bp.route('/canchas/<id>', methods=['PATCH'])
def patch_cancha(id):
    try:
        id_cancha = validar_id_cancha(id)
    except ValueError as e:
        return jsonify(e.args[0]), 400

    body = request.get_json(silent=True)

    if body is None:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Cuerpo de la solicitud inválido',
            description='El cuerpo debe ser un JSON válido con Content-Type application/json'
        )), 400

    try:
        cancha = canchas_service.actualizar_cancha_parcial(id_cancha, body)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status

    return jsonify(cancha)


@canchas_bp.route('/canchas/<id>', methods=['DELETE'])
def delete_cancha(id):
    try:
        id_cancha = validar_id_cancha(id)
    except ValueError as e:
        return jsonify(e.args[0]), 400

    try:
        canchas_service.eliminar_cancha(id_cancha)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status

    return '', 204


@canchas_bp.route('/canchas/disponibles', methods=['GET'])
def get_canchas_disponibles():
    try:
        params = validar_params_disponibles(request.args.to_dict())
    except ValueError as e:
        return jsonify(e.args[0]), 400

    canchas, total = canchas_service.listar_canchas_disponibles(params)

    response = construir_respuesta_paginada(
        datos={'canchas': canchas},
        total=total,
        offset=params['offset'],
        limit=params['limit'],
        base_url=request.base_url,
        params=request.args.to_dict()
    )

    return jsonify(response)
