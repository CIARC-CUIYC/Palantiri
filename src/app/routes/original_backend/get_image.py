from flask import Blueprint, request, send_file
from src.app.models.melvin import melvin
from werkzeug.exceptions import BadRequest
from PIL import Image
import io

bp = Blueprint('image', __name__, url_prefix='/image')


@bp.route('/', methods=['GET'])
def get_image():
    try:
        melvin_pos = melvin.pos
        angle = melvin.camera_angle
        # TODO: implement image access
        img = get_map_chunk(melvin_pos, angle.get_side_length())
        img_byte_array = io.BytesIO()
        img.save(img_byte_array, format='PNG')
        img_byte_array.seek(0)

        return send_file(img_byte_array, mimetype='image/png')
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}, 500
