from _typeshed import Incomplete

xpixels: Incomplete
ypixels: Incomplete
YBORDER: float
XBORDER: Incomplete
STD_SCALE: int
FAKE_NOISE: float
THICCNESS: int
BIN_WIDTH: float
NUM_BINS: Incomplete
WIDTH: Incomplete

def gaussian_2d(width, height, h, k, a, b): ...
def gaussian_1d(width, height, h, k, ystd, xwidth): ...
def scaling2pix(x, y, bounds): ...
def coords2pix(x, y, bounds): ...
def write_image(data, filename) -> None: ...
def dress_image(img, bounds): ...
def points2img(fname) -> None: ...
