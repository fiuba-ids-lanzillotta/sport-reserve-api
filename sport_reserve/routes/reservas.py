from flask import Blueprint, jsonify, request
from ..constants import ERROR_CODE_INVALID_BODY
from ..utils import construir_error_api
from ..pagination import construir_respuesta_paginada
from ..validators.reservas import validar_params_reservas, validar_id_reserva
from ..services import reservas as reservas_service

reservas_bp = Blueprint('reservas', __name__)


@reservas_bp.route('/reservas', methods=['GET'])
def get_reservas():
    try:
        params = validar_params_reservas(request.args.to_dict())
    except ValueError as e:
        return jsonify(e.args[0]), 400

    reservas, total = reservas_service.listar_reservas(params)

    if total == 0:
        return '', 204

    response = construir_respuesta_paginada(
        datos={'reservas': reservas},
        total=total,
        offset=params['offset'],
        limit=params['limit'],
        base_url=request.base_url,
        params=request.args.to_dict()
    )

    return jsonify(response)


@reservas_bp.route('/reservas', methods=['POST'])
def post_reserva():
    body = request.get_json(silent=True)

    if body is None:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Cuerpo de la solicitud inválido',
            description='El cuerpo debe ser un JSON válido con Content-Type application/json'
        )), 400

    try:
        reservas_service.crear_reserva(body)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status

    return '', 201


@reservas_bp.route('/reservas/<id>', methods=['GET'])
def get_reserva_por_id(id):
    try:
        id_reserva = validar_id_reserva(id)
    except ValueError as e:
        return jsonify(e.args[0]), 400

    reserva = reservas_service.buscar_reserva_por_id(id_reserva)

    if not reserva:
        return jsonify(construir_error_api(
            code='reserva.not.found',
            message='Reserva no encontrada',
            description=f"No existe una reserva con id '{id_reserva}'"
        )), 404

    return jsonify(reserva)


@reservas_bp.route('/reservas/<id>/estado', methods=['PUT'])
def put_estado_reserva(id):
    try:
        id_reserva = validar_id_reserva(id)
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
        reservas_service.cambiar_estado_reserva(id_reserva, body)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status

    return '', 204
