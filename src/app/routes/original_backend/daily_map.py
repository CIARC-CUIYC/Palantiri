import logging
from typing import Tuple

from flask import Blueprint, request, jsonify
from PIL import Image, ImageChops

from src.app.image_loader import get_full_map

bp = Blueprint('dailyMap', __name__)


@bp.route('/dailyMap', methods=['POST'])
def upload_daily_map() -> Tuple[dict, int]:
    """
    Handle POST upload of a daily map image and compare it with the original.

    Expects:
        A multipart/form-data request with an 'image' field.

    Returns:
        Tuple[dict, int]: JSON response and HTTP status code.
    """
    try:
        uploaded_file = request.files.get('image')
        if not uploaded_file:
            return {"error": "No file uploaded."}, 400

        file_stream = uploaded_file.stream
        uploaded_img = Image.open(file_stream)
        original_map  = get_full_map()

        diff = ImageChops.difference(uploaded_img, original_map)
        mean_diff = sum(list(diff.getdata())) / (uploaded_img.width * uploaded_img.height * 3)

        logger = logging.getLogger(__name__)
        logger.info(f"Daily Map submitted. Mean difference: {mean_diff}")

        return jsonify("upload successful"), 200
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}, 500

