from flask import Blueprint, jsonify, request
from ..constants import ERROR_CODE_INVALID_BODY
from ..utils import construir_error_api
from ..pagination import construir_respuesta_paginada
from ..validators.bloqueos import validar_params_bloqueos, validar_id_bloqueo
from ..services import bloqueos as bloqueos_service

bloqueos_bp = Blueprint('bloqueos', __name__)


@bloqueos_bp.route('/bloqueos', methods=['GET'])
def get_bloqueos():
    try:
        params = validar_params_bloqueos(request.args.to_dict())
    except ValueError as e:
        return jsonify(e.args[0]), 400

    bloqueos, total = bloqueos_service.listar_bloqueos(params)

    if total == 0:
        return '', 204

    response = construir_respuesta_paginada(
        datos={'bloqueos': bloqueos},
        total=total,
        offset=params['offset'],
        limit=params['limit'],
        base_url=request.base_url,
        params=request.args.to_dict()
    )

    return jsonify(response)


@bloqueos_bp.route('/bloqueos', methods=['POST'])
def post_bloqueo():
    body = request.get_json(silent=True)

    if body is None:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Cuerpo de la solicitud inválido',
            description='El cuerpo debe ser un JSON válido con Content-Type application/json'
        )), 400

    try:
        bloqueos_service.crear_bloqueo(body)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400

        return jsonify(e.args[0]), status

    return '', 201


@bloqueos_bp.route('/bloqueos/<id>', methods=['DELETE'])
def delete_bloqueo(id):
    try:
        id_bloqueo = validar_id_bloqueo(id)
    except ValueError as e:
        return jsonify(e.args[0]), 400

    try:
        bloqueos_service.eliminar_bloqueo(id_bloqueo)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400

        return jsonify(e.args[0]), status

    return '', 204
