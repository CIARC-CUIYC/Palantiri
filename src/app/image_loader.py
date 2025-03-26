from io import BytesIO
import tempfile
import cairo
from PIL import Image

Image.MAX_IMAGE_PIXELS = 933120000

from src.app.constants import MAP_HEIGHT, MAP_WIDTH

from ctypes import CDLL, POINTER, Structure, byref, util
from ctypes import c_bool, c_byte, c_void_p, c_int, c_double, c_uint32, c_char_p


class _PycairoContext(Structure):
    _fields_ = [
        ("PyObject_HEAD", c_byte * object.__basicsize__),
        ("ctx", c_void_p),
        ("base", c_void_p),
    ]


class _RsvgProps(Structure):
    _fields_ = [("width", c_int), ("height", c_int), ("em", c_double), ("ex", c_double)]


class _GError(Structure):
    _fields_ = [("domain", c_uint32), ("code", c_int), ("message", c_char_p)]


def _load_rsvg(rsvg_lib_path=None, gobject_lib_path=None):
    if rsvg_lib_path is None:
        rsvg_lib_path = util.find_library("rsvg-2")
    if gobject_lib_path is None:
        gobject_lib_path = util.find_library("gobject-2.0")
    l = CDLL(rsvg_lib_path)
    g = CDLL(gobject_lib_path)
    g.g_type_init()

    l.rsvg_handle_new_from_file.argtypes = [c_char_p, POINTER(POINTER(_GError))]
    l.rsvg_handle_new_from_file.restype = c_void_p
    l.rsvg_handle_render_cairo.argtypes = [c_void_p, c_void_p]
    l.rsvg_handle_render_cairo.restype = c_bool
    l.rsvg_handle_get_dimensions.argtypes = [c_void_p, POINTER(_RsvgProps)]

    return l


_librsvg = _load_rsvg()


class Handle(object):
    def __init__(self, path):
        lib = _librsvg
        err = POINTER(_GError)()
        self.handle = lib.rsvg_handle_new_from_file(path.encode(), byref(err))
        if self.handle is None:
            gerr = err.contents
            raise Exception(gerr.message)
        self.props = _RsvgProps()
        lib.rsvg_handle_get_dimensions(self.handle, byref(self.props))

    def get_dimension_data(self):
        svgDim = self.RsvgDimensionData()
        _librsvg.rsvg_handle_get_dimensions(self.handle, byref(svgDim))
        return (svgDim.width, svgDim.height)

    def render_cairo(self, ctx):
        """Returns True is drawing succeeded."""
        z = _PycairoContext.from_address(id(ctx))
        return _librsvg.rsvg_handle_render_cairo(self.handle, z.ctx)


PADDING = 600


def load_map_image() -> Image:
    img = cairo.ImageSurface(cairo.FORMAT_ARGB32, MAP_WIDTH, MAP_HEIGHT)
    ctx = cairo.Context(img)
    handle = Handle("../test_image.svg")
    handle.render_cairo(ctx)

    with tempfile.NamedTemporaryFile(suffix=".png") as f:
        img.write_to_png(f)
        base_image = Image.open(f.name)
    image = Image.new("RGB", (MAP_WIDTH + (2 * PADDING), MAP_HEIGHT + (2 * PADDING)))

    # center
    image.paste(base_image, (PADDING, PADDING))

    # left
    image.paste(
        base_image.crop((MAP_WIDTH - PADDING, 0, MAP_WIDTH, MAP_HEIGHT - 1)),
        (0, PADDING),
    )
    # right
    image.paste(
        base_image.crop((0, 0, PADDING, MAP_HEIGHT)), (MAP_WIDTH + PADDING, PADDING)
    )
    # top
    image.paste(
        image.crop((0, MAP_HEIGHT, MAP_WIDTH + (2 * PADDING), MAP_HEIGHT + PADDING)),
        (0, 0),
    )
    # bottom
    image.paste(
        image.crop((0, 0, MAP_WIDTH + (2 * PADDING), PADDING)),
        (0, MAP_HEIGHT + PADDING),
    )

    return image


map_image = load_map_image()


def get_map_chunk(center_pos: tuple[int, int], size: int) -> bytes:
    assert (size / 2) < PADDING

    center_left, center_top = center_pos

    offset_left = center_left - size / 2
    offset_top = center_top - size / 2
    image_bytes = BytesIO()
    map_image.crop(
        (
            offset_left + PADDING,
            offset_top + PADDING,
            offset_left + PADDING + size,
            offset_top + PADDING + size,
        )
    ).save(image_bytes, format="PNG")
    return image_bytes.getvalue()
