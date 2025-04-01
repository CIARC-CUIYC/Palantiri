import logging
from io import BytesIO
import tempfile
from typing import Tuple, Optional, Any

import cairo
from PIL import Image
from PIL.Image import Image as PILImage

Image.MAX_IMAGE_PIXELS = 933120000

from src.app.constants import MAP_HEIGHT, MAP_WIDTH

from ctypes import CDLL, POINTER, Structure, byref, util
from ctypes import c_bool, c_byte, c_void_p, c_int, c_double, c_uint32, c_char_p


# --- Internal ctypes binding to librsvg ---
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


def _load_rsvg(rsvg_lib_path: Optional[str] = None, gobject_lib_path: Optional[str] = None) -> CDLL:
    if rsvg_lib_path is None:
        rsvg_lib_path = util.find_library("rsvg-2")
    if gobject_lib_path is None:
        gobject_lib_path = util.find_library("gobject-2.0")

    l: CDLL = CDLL(rsvg_lib_path)
    g: CDLL = CDLL(gobject_lib_path)

    g.g_type_init()

    l.rsvg_handle_new_from_file.argtypes = [c_char_p, POINTER(POINTER(_GError))]
    l.rsvg_handle_new_from_file.restype = c_void_p
    l.rsvg_handle_render_cairo.argtypes = [c_void_p, c_void_p]
    l.rsvg_handle_render_cairo.restype = c_bool
    l.rsvg_handle_get_dimensions.argtypes = [c_void_p, POINTER(_RsvgProps)]

    return l


_librsvg = _load_rsvg()


# --- SVG Handle wrapper ---
class Handle(object):
    """
    Wrapper for rendering SVG images with librsvg and Pycairo.
    """

    def __init__(self, path: str) -> None:
        lib = _librsvg
        err = POINTER(_GError)()
        self.handle = lib.rsvg_handle_new_from_file(path.encode(), byref(err))
        if self.handle is None:
            gerr = err.contents
            raise Exception(gerr.message)
        self.props = _RsvgProps()
        lib.rsvg_handle_get_dimensions(self.handle, byref(self.props))

    def get_dimension_data(self) -> Tuple[int, int]:
        """
        Returns:
            Tuple[int, int]: Width and height of the SVG image.
        """
        props = _RsvgProps()
        _librsvg.rsvg_handle_get_dimensions(self.handle, byref(props))
        return props.width, props.height
        # CHRIS Artifacts
        # svgDim = self.RsvgDimensionData()
        # _librsvg.rsvg_handle_get_dimensions(self.handle, byref(svgDim))
        # return svgDim.width, svgDim.height

    # NOTE: the type hint 'Any' here is because mypy doesnt accept cairo.Context
    def render_cairo(self, ctx: Any) -> bool:
        """
        Render SVG to a Cairo context.
        Returns True is drawing succeeded

        Args:
            ctx (cairo.Context): Target context.

        Returns:
            bool: Success flag.
        """

        z: _PycairoContext = _PycairoContext.from_address(id(ctx))
        result: bool = _librsvg.rsvg_handle_render_cairo(self.handle, z.ctx)
        return result

        # CHRIS Artifacts
        # z = _PycairoContext.from_address(id(ctx))
        # return _librsvg.rsvg_handle_render_cairo(self.handle, z.ctx)


PADDING = 600


# --- Map generation and overlay handling ---
def load_map_image() -> PILImage:
    """
    Load and render the base map from SVG, then pad and tile it for wraparound.

    Returns:
        Image.Image: A padded and wrapped version of the rendered map.
    """
    img = cairo.ImageSurface(cairo.FORMAT_ARGB32, MAP_WIDTH, MAP_HEIGHT)
    ctx = cairo.Context(img)
    handle = Handle("assets/test_image.svg")
    handle.render_cairo(ctx)

    # CHRIS artifact
    # with tempfile.NamedTemporaryFile(suffix=".png") as f:
    #    img.write_to_png(f)
    #    base_image = Image.open(f.name)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img.write_to_png(f.name)
        base_image = Image.open(f.name).convert("RGB")

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


def_map_image = load_map_image()
current_map_image = def_map_image.copy()
obj_image = Image.open("assets/obj_img.png").convert("RGBA")


def get_obj_img() -> PILImage:
    """
    Returns:
        Image.Image: The objective marker image (RGBA).
    """
    return obj_image


def get_map_chunk(center_pos: tuple[int, int], size: int) -> bytes:
    """
    Crop a square region of the map around a given position.

    Args:
        center_pos (Tuple[int, int]): (x, y) center of the crop.
        size (int): Side length of the square.

    Returns:
        bytes: PNG bytes of the cropped image.
    """
    assert (size / 2) < PADDING

    center_left, center_top = center_pos

    offset_left = center_left - size / 2
    offset_top = center_top - size / 2
    image_bytes = BytesIO()
    current_map_image.crop(
        (
            offset_left + PADDING,
            offset_top + PADDING,
            offset_left + PADDING + size,
            offset_top + PADDING + size,
        )
    ).save(image_bytes, format="PNG")
    return image_bytes.getvalue()


def get_full_map() -> PILImage:
    """
    Returns:
        Image.Image: The full, wrapped current map image.
    """
    return current_map_image


def apply_map_overlay(overlay: PILImage) -> None:
    """
    Blend an RGBA overlay onto the current map image using its alpha channel.

    Args:
        overlay (Image.Image): The overlay image to apply.

    Raises:
        ValueError: If dimensions do not match.
    """
    (width, height) = overlay.size
    if width != (MAP_WIDTH + 2 * PADDING) or height != (MAP_HEIGHT + 2 * PADDING):
        logging.getLogger(__name__).info(f"width: {width}, height: {height}")
        raise ValueError("Overlay must be the same size as the map")
    alpha = overlay.split()[3]
    current_map_image.paste(overlay, (0, 0), mask=alpha)


def remove_map_overlay(overlay: PILImage) -> None:
    """
    Restore the default map underneath the masked region defined by an overlay.

    Args:
        overlay (Image.Image): An RGBA overlay to remove.

    Raises:
        ValueError: If dimensions do not match.
    """
    (width, height) = overlay.size
    if width != MAP_WIDTH or height != MAP_HEIGHT:
        raise ValueError("Overlay must be the same size as the map")
    mask_img = overlay.convert("L")
    # Extract the masked portion
    masked_region = Image.composite(def_map_image, Image.new("RGBA", def_map_image.size), mask_img)

    # Paste into destination image
    current_map_image.paste(masked_region, (0, 0), mask_img)
