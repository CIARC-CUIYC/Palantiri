from typing import Tuple

from flask import Blueprint, send_file, Response
from src.app.image_loader import get_map_chunk
from src.app.models.melvin import melvin
import io

bp = Blueprint('image', __name__)


@bp.route('/image', methods=['GET'])
def get_image() -> Response:
    """
    Return a cropped map image based on Melvin's position and camera angle.

    Returns:
        Response: PNG image stream or JSON error message with status code.
    """
    try:
        melvin_pos: Tuple[int, int] = (round(melvin.pos[0]), round(melvin.pos[1]))
        angle = melvin.camera_angle
        img = get_map_chunk(melvin_pos, angle.get_side_length())
        img_stream = io.BytesIO(img)
        return send_file(img_stream, mimetype='image/png')
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}, 500
