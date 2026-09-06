from flask import Blueprint, jsonify
from ..services import deportes as deportes_service

deportes_bp = Blueprint('deportes', __name__)


@deportes_bp.route('/deportes', methods=['GET'])
def get_deportes():
    deportes = deportes_service.listar_deportes()
    return jsonify({'deportes': deportes})
