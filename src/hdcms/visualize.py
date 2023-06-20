# https://stackoverflow.com/questions/49829783/draw-a-gradual-change-ellipse-in-skimage

import numpy as np
import sys
import matplotlib.pyplot as plt
from PIL import Image

class ImageConfig:
    """this class is used to keep track of all the parameters of the image
    """
    def __init__(self, size=(3600, 1200), std_scale=1, desingularization=1e-5, axis_thickness=3, xlabel="m/z values", ylabel="intensities", title="hdc visualization"):
        self.xpixels, self.ypixels = size

        # how much to scale the stddev
        self.std_scale = std_scale
        # how much to add to the stddev after scale
        self.desingularization = desingularization

        # thickness of axes
        self.axis_thickness = axis_thickness

        self.xlabel = xlabel
        self.ylabel = ylabel
        self.title = title

class StatsContext:
    """this class is used by 1d code to keep track of the bin parameters
    """
    def __init__(self, start=0, stop=899.9, num_bins=9000):
        self.start = start
        self.stop = stop
        self.num_bins = num_bins
        self.bin_width = (stop - start) / (num_bins - 1)

def gaussian_2d(width, height, h, k, a, b):
    """ goal: output an array of pixels with 2d gaussian drawn on
    recall: a 2d gaussian is a mean and standard deviation of a peak

    width and height are from the image config [refactor: pass the config itself and use field access]
    (h,k) are the center of the gaussian
    (a, b) are the standard deviations of the gaussian
    """
    # Generate (x,y) coordinate arrays
    y,x = np.mgrid[-k:height-k,-h:width-h] 
    # returns an array [[[-k, -k+1, ..., height-k-1, height-k], ...], 
    #                   [[-k, ..., -k], ..., [height-k, ..., height-k]]]

    weights = np.exp((-1/2) * ((x / a)**2 + ((y / b)**2)))
    if np.max(weights):
        return weights / np.max(weights)
    else:
        return weights

def gaussian_1d(h, k, ystd, xwidth, config):
    """ goal: output an array of pixels with 1d gaussian drawn on
    recall: a 1d gaussian is a mean and standard deviation of a bin

    (h,k) are the center of the gaussian
    ystd is the standard deviation of the gaussian
    xwidth is how wide the bin is
    config is the image config (size, etc)
    """
    # don't want to go off screen
    lowest_x_rendered = max(int(h - (xwidth/2)), 0)
    highest_x_rendered = min(int(h + (xwidth/2)), config.xpixels)
    if lowest_x_rendered == highest_x_rendered:
        print(f"pixels {(h,k)} w ystd: {ystd}, bin_width: {xwidth} in image of size {(config.xpixels, config.ypixels)} (width, height), ", file=sys.stderr)
        return np.zeros((config.ypixels, config.xpixels))
    y,_ = np.mgrid[-k:config.ypixels-k, lowest_x_rendered:highest_x_rendered]
    # so sets y to [[-k, -k, -k, ..., -k, -k],
    #               [-(k-1), -(k-1), -(k-1), ..., -(k-1)],
    #               ...
    #               [(height-k-1), (height-k-1), ..., (height-k-1)]]
    # with the number of columns equal to (highest_x_rendered - lowest_x_rendered)
    weights = np.exp((-1/2) * ((y / ystd)**2))

    ret = np.zeros((config.ypixels, config.xpixels))
    ret[:, lowest_x_rendered:highest_x_rendered] = weights
    if weights.size != 0 and np.max(weights) != 0:
        return ret / np.max(weights)
    else:
        return ret

def coordinate_rectangle_to_pixels(rect, axis_limits, config):
    """ goal: convert (x,y,width,height) from coordinates to pixel
    note: we need to flip the y values
    """
    x, y, width, height = rect
    xmin, ymin, xmax, ymax = axis_limits
    xscale = config.xpixels / (xmax - xmin)
    yscale = config.ypixels / (ymax - ymin)

    x = (x - xmin)*xscale # we don't add anything bc min pixel value is 0
    y = (y - ymin)*yscale # we don't add anything bc min pixel value is 0
    return (x, config.ypixels - y, width * xscale, height * yscale)

def write_image(data, color=(1, 0, 0), config=ImageConfig(), context=StatsContext(), axis_limits=None):
    data = np.array(data)
    if len(data[0]) == 4:
        data[:,2] = data[:,2] * config.std_scale + config.desingularization
        data[:,3] = data[:,3] * config.std_scale + config.desingularization
    elif len(data[0]) == 2:
        data[:,1] = data[:,1] * config.std_scale + config.desingularization
    else:
        raise RuntimeError(f"Incorrect dimension: recieved {data.shape} must be nx2 or nx4")

    # We need to auto adjust the axis limits if not provided
    if not axis_limits:
        yborder = 0.1
        xborder = 0.1

        if len(data[0]) == 4:
            width = np.max(data[:, 0]) - np.min(data[:, 0])
            height = np.max(data[:, 1]) - np.min(data[:, 1])
        else:
            width = (np.max(np.nonzero(data[:, 0])) + 1) * context.bin_width
            height = np.max(data[:, 0])
        # min_x, min_y, max_x, max_y
        axis_limits = (width * (-xborder), height * (-yborder), width * (1+xborder), height * (1+yborder))

    if len(data[0]) == 4:
        assert(np.min(data[:, 1]) >= 0 and np.min(data[:,0]) >= 0)

    img = np.ones((config.ypixels, config.xpixels, 3))

    for i, peak in enumerate(data):
        if len(peak) == 4:
            h, k, a, b = coordinate_rectangle_to_pixels(peak, axis_limits, config)
            red, green, blue = color
            img -= (1-red) * gaussian_2d(config.xpixels, config.ypixels, h, k, a, b)
            img -= (1-green) * gaussian_2d(config.xpixels, config.ypixels, h, k, a, b)
            img -= (1-blue) * gaussian_2d(config.xpixels, config.ypixels, h, k, a, b)
        else:
            if np.sum(peak[0]) != 0.:
                rect_center_x = context.start + i*context.bin_width + context.bin_width/2
                h, k, width, sd = coordinate_rectangle_to_pixels((rect_center_x, peak[0], context.bin_width, peak[1]), axis_limits, config)
                red, green, blue = color
                img[:, :, 0] -= (1-red) * gaussian_1d(h, k, sd, width, config)
                img[:, :, 1] -= (1-green) * gaussian_1d(h, k, sd, width, config)
                img[:, :, 2] -= (1-blue) * gaussian_1d(h, k, sd, width, config)

    img = dress_image(img, axis_limits, config)
    return Image.fromarray(img)

def dress_image(img, axis_limits, config):
    """this function takes the straight output of the gaussians and adds axes, tickmarks, text
    """
    # convert to bytes 0..1 -> 0..255
    img = np.uint8(img * 255)

    xmin, ymin, xmax, ymax = axis_limits
    xlen = img.shape[1]
    ylen = img.shape[0]
    old_figure_num = plt.gcf().number # figure to restore
    figsize = plt.rcParams["figure.figsize"][0] # we take x value
    APPROX_MARGIN_RATIO_OF_IMG = 0.3 # correct for the fact that plt tick marks and axes take up part of image
    fig, ax = plt.subplots(dpi=(1/APPROX_MARGIN_RATIO_OF_IMG)*ylen/figsize)
    ax.imshow(img, extent=(xmin, xmax, ymin, ymax))
    ax.set_aspect(((xmax-xmin)/(ymax-ymin))/(xlen/ylen))
    ax.set_title(config.title)
    ax.set_xlabel(config.xlabel)
    ax.set_ylabel(config.ylabel)

    fig.canvas.draw()
    buf = fig.canvas.tostring_rgb()
    ncols, nrows = fig.canvas.get_width_height()
    img = np.frombuffer(buf, dtype=np.uint8)
    # note: the nrows and ncols order
    img = img.reshape(nrows, ncols, 3)

    # reactivate old figure
    plt.figure(old_figure_num)
    return img
