from flask import Blueprint, request
from PIL import Image

bp = Blueprint('dailyMap', __name__, url_prefix='/dailyMap')


@bp.route('/', methods=['POST'])
def upload_daily_map():
    try:
        uploaded_file = request.files.get('image')
        if not uploaded_file:
            return {"error": "No file uploaded."}, 400

        file_stream = uploaded_file.stream
        img = Image.open(file_stream)
        map_chunk()

        return "upload successful", 200
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}, 500

