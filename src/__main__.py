from .app import create_app
from .app.image_loader import load_map_image

load_map_image()

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
