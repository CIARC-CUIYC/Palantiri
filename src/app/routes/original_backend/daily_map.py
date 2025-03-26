import logging

from flask import Blueprint, request
from PIL import Image, ImageChops

from src.app.image_loader import get_full_map

bp = Blueprint('dailyMap', __name__, url_prefix='/dailyMap')


@bp.route('/', methods=['POST'])
def upload_daily_map():
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

        return "upload successful", 200
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}, 500

