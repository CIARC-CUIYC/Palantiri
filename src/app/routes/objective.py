from flask import Blueprint, request, jsonify
from src.app.models.obj_manager import obj_manager

bp = Blueprint('objective', __name__, url_prefix='/objective')

@bp.route('/', methods=['GET'])
def objective():
    print(jsonify(obj_manager.get_all_objectives()))
    return jsonify(obj_manager.get_all_objectives())