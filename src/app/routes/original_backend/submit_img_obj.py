from flask import Blueprint, send_file, request
from src.app.models.melvin import melvin
from PIL import Image, ImageChops
import logging

from src.app.models.obj_manager import obj_manager

bp = Blueprint('image', __name__, url_prefix='/image')


@bp.route('/', methods=['POST'])
def submit_img_obj():
    try:
        obj_id = int(request.args.get('objective_id'))
        uploaded_file = request.files.get('image')
        if not uploaded_file:
            return {"error": "No file uploaded."}, 400

        file_stream = uploaded_file.stream
        uploaded_img = Image.open(file_stream)
        actual_img = obj_manager.get_obj_img(obj_id)

        diff = ImageChops.difference(uploaded_img, actual_img)
        mean_diff = sum(list(diff.getdata())) / (actual_img.width * actual_img.height * 3)

        obj_manager.delete_objective_by_id(obj_id)
        logger = logging.getLogger(__name__)
        logger.info(f"Objective {obj_id} submitted. Mean difference: {mean_diff}")
        return "received objective", 200
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}, 500
