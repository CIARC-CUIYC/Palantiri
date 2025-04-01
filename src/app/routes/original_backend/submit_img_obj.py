from flask import request, jsonify
from PIL import Image
import logging

from src.app.models.obj_manager import obj_manager
from src.app.routes.original_backend.get_image import bp


@bp.route('/image', methods=['POST'])
def submit_img_obj() -> tuple[object, int]:
    """
    Handle a submitted image for a specific objective.
    (Future: Compare the submitted image to the expected one.)

    Query Params:
        objective_id (int): The ID of the objective being submitted.

    Form Data:
        image (file): The uploaded image file.

    Returns:
        Tuple[object, int]: Confirmation JSON and HTTP status code.
    """
    try:
        obj_id = int(request.args.get('objective_id'))
        uploaded_file = request.files.get('image')
        if not uploaded_file:
            return {"error": "No file uploaded."}, 400

        file_stream = uploaded_file.stream
        uploaded_img = Image.open(file_stream)
        #actual_img = obj_manager.get_obj_img(obj_id)

        #diff = ImageChops.difference(uploaded_img, actual_img)
        #mean_diff = sum(list(diff.getdata())) / (actual_img.width * actual_img.height * 3)

        obj_manager.delete_objective_by_id(obj_id)
        logger = logging.getLogger(__name__)
        logger.info(f"Objective {obj_id} submitted. Mean difference: not computed yet")
        return jsonify("received objective"), 200
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}, 500
