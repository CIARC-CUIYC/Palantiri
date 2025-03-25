from flask import Blueprint, jsonify
from app.models.melvin import melvin

bp = Blueprint('reset', __name__, url_prefix='/reset')

@bp.route('/', methods=['GET'])
def reset():
    melvin.reset()
    return jsonify({"message": "Melvin has been reset."})