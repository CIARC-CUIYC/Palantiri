from src.app import create_app
from src.app.image_loader import load_map_image

load_map_image()

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)
