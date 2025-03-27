from flask import Blueprint, jsonify
from src.app.models.melvin import melvin

bp = Blueprint('reset', __name__)

@bp.route('/reset', methods=['GET'])
def reset():
    melvin.reset()
    return jsonify("Reset the engine successfully."), 200