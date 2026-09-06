from flask import Blueprint, jsonify, request
from ..constants import ERROR_CODE_INVALID_BODY
from ..utils import construir_error_api
from ..pagination import construir_respuesta_paginada
from ..validators.socios import validar_params_socios, validar_id_socio
from ..services import socios as socios_service

socios_bp = Blueprint('socios', __name__)


@socios_bp.route('/socios', methods=['GET'])
def get_socios():
    try:
        params = validar_params_socios(request.args.to_dict())
    except ValueError as e:
        return jsonify(e.args[0]), 400

    socios, total = socios_service.listar_socios(params)

    response = construir_respuesta_paginada(
        datos={'socios': socios},
        total=total,
        offset=params['offset'],
        limit=params['limit'],
        base_url=request.base_url,
        params=request.args.to_dict()
    )

    return jsonify(response)


@socios_bp.route('/socios', methods=['POST'])
def post_socio():
    body = request.get_json(silent=True)

    if body is None:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Cuerpo de la solicitud inválido',
            description='El cuerpo debe ser un JSON válido con Content-Type application/json'
        )), 400

    try:
        socio = socios_service.crear_socio(body)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status

    return jsonify(socio), 201


@socios_bp.route('/socios/<id>', methods=['GET'])
def get_socio_por_id(id):
    try:
        id_socio = validar_id_socio(id)
    except ValueError as e:
        return jsonify(e.args[0]), 400

    socio = socios_service.buscar_socio_por_id(id_socio)

    if not socio:
        return jsonify(construir_error_api(
            code='socio.not.found',
            message='Socio no encontrado',
            description=f"No existe un socio con id '{id_socio}'"
        )), 404

    return jsonify(socio)


@socios_bp.route('/socios/<id>', methods=['PATCH'])
def patch_socio(id):
    try:
        id_socio = validar_id_socio(id)
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
        socio = socios_service.actualizar_socio_parcial(id_socio, body)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status

    return jsonify(socio)
