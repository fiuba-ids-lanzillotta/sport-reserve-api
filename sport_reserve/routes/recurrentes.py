from flask import Blueprint, jsonify, request
from ..constants import ERROR_CODE_INVALID_BODY
from ..utils import construir_error_api
from ..services import recurrentes as recurrentes_service

recurrentes_bp = Blueprint('recurrentes', __name__)


@recurrentes_bp.route('/reservas/recurrentes', methods=['POST'])
def post_reservas_recurrentes():
    body = request.get_json(silent=True)

    if body is None:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Cuerpo de la solicitud inválido',
            description='El cuerpo debe ser un JSON válido con Content-Type application/json'
        )), 400

    try:
        recurrentes_service.crear_reservas_recurrentes(body)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400

        return jsonify(e.args[0]), status

    return '', 201
