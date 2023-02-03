# https://stackoverflow.com/questions/49829783/draw-a-gradual-change-ellipse-in-skimage

import cv2
import numpy as np
import sys

class ImageConfig:
    # designed to be called by write(), so it's very coupled
    def __init__(self, size=(3600, 1200), std_scale=1, desingularization=1e-5, axis_thickness=3):
        self.xpixels, self.ypixels = size

        # how much to scale the stddev
        self.std_scale = std_scale
        # how much to add to the stddev after scale
        self.desingularization = desingularization

        # thickness of axes
        self.axis_thickness = axis_thickness

class StatsContext:
    def __init__(self, start=0, stop=899.9, num_bins=9000):
        self.start = start
        self.stop = stop
        self.num_bins = num_bins
        self.bin_width = (stop - start) / (num_bins - 1)

def gaussian_2d(width, height, h, k, a, b):
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

# overall goal: convert (x,y,width,height) from coordinates to pixel
# note: we need to flip the y values
def coordinate_rectangle_to_pixels(rect, axis_limits, config):
    x, y, width, height = rect
    xmin, ymin, xmax, ymax = axis_limits
    xscale = config.xpixels / (xmax - xmin)
    yscale = config.ypixels / (ymax - ymin)

    x = (x - xmin)*xscale # we don't add anything bc min pixel value is 0
    y = (y - ymin)*yscale # we don't add anything bc min pixel value is 0
    return (x, config.ypixels - y, width * xscale, height * yscale)

def write_image(data, filename, config=ImageConfig(), context=StatsContext(), axis_limits=None):
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
            height = np.max(data[:, 0]) - np.min(data[:, 0])
        else:
            width = (np.max(np.nonzero(data[:, 0])) + 1) * context.bin_width
            height = np.max(data[:, 0])
        # min_x, min_y, max_x, max_y
        axis_limits = (width * (-xborder), height * (-yborder), width * (1+xborder), height * (1+yborder))

    if len(data[0]) == 4:
        assert(np.min(data[:, 1]) >= 0 and np.min(data[:,0]) >= 0)

    img = np.zeros((config.ypixels, config.xpixels))

    for i, peak in enumerate(data):
        if len(peak) == 4:
            h, k, a, b = coordinate_rectangle_to_pixels(peak, axis_limits, config)
            img += gaussian_2d(config.xpixels, config.ypixels, h, k, a, b)
        else:
            if np.sum(peak[0]) != 0.:
                rect_center_x = context.start + i*context.bin_width + context.bin_width/2
                h, k, width, sd = coordinate_rectangle_to_pixels((rect_center_x, peak[0], context.bin_width, peak[1]), axis_limits, config)
                img += gaussian_1d(h, k, sd, width, config)

    img = dress_image(img, axis_limits, config)

    cv2.imwrite(filename, img)

# this function takes the straight output of the gaussians and adds axes, tickmarks, text
def dress_image(img, axis_limits, config):
    # invert -> most of image is ~1, and peaks are ~0
    img = np.clip(1 - img, 0, 1)

    # convert to B, G, R image rather than just single channel black and white
    one = np.ones(img.shape)
    img = cv2.merge((img, img, one)) # causes red to fill in peak areas

    # convert to bytes 0..1 -> 0..255
    img = np.uint8(img * 255)

    xmin, ymin, xmax, ymax = axis_limits
    # xaxis
    if ymin <= 0 and 0 < ymax:
        startx, starty, _, _ = coordinate_rectangle_to_pixels((xmin, 0, 0, 0), axis_limits, config)
        endx, endy, _, _ = coordinate_rectangle_to_pixels((xmax, 0, 0, 0), axis_limits, config)
        cv2.line(img, (int(startx), int(starty)), (int(endx), int(endy)), color=(0, 0, 0), thickness=config.axis_thickness)
    # yaxis
    if xmin <= 0 and 0 < xmax:
        startx, starty, _, _ = coordinate_rectangle_to_pixels((0, ymin, 0, 0), axis_limits, config)
        endx, endy, _, _ = coordinate_rectangle_to_pixels((0, ymax, 0, 0), axis_limits, config)
        cv2.line(img, (int(startx), int(starty)), (int(endx), int(endy)), color=(0, 0, 0), thickness=config.axis_thickness)

    # draw ticks and labels
    thickness = max(int((config.xpixels+config.ypixels)/1200), 1)
    label_config = {
        'fontFace': cv2.FONT_HERSHEY_SIMPLEX,
        'color': (0,0,0),
        # 1 at 800x400, 4 at 3600x1200
        'thickness': thickness,
        # 1 at 800x400, 2 at 3600x1200
        'fontScale': int(config.axis_thickness*(2/3)),
    }
    tick_config = {
        'color': (0,0,0),
        'thickness': thickness,
    }
    tick_len = config.axis_thickness * 5
    tick_y_value = (ymax - ymin) / 1.2
    tick_x_value = (xmax - xmin) / 1.2

    # x-axis tick mark
    tick_x, tick_y, _, _ = coordinate_rectangle_to_pixels((tick_x_value, 0, 0, 0), axis_limits, config)
    # tick
    cv2.line(img, (int(tick_x), int(tick_y)), (int(tick_x), int(tick_y + tick_len)), **tick_config)
    # label
    text = str(int(tick_x_value*10) / 10)
    cv2.putText(img, text, (int(tick_x - 12 * tick_len), int(tick_y + 3.5 * tick_len)), **label_config)

    # y-axis tick mark
    tick_x, tick_y, _, _ = coordinate_rectangle_to_pixels((0, tick_y_value, 0, 0), axis_limits, config)
    # tick
    cv2.line(img, (int(tick_x - tick_len), int(tick_y)), (int(tick_x), int(tick_y)), **tick_config)
    # label
    text = str(int(tick_y_value*100) / 100)
    cv2.putText(img, text, (int(tick_x - 5*tick_len), int(tick_y + 5*tick_len)), **label_config)
    return img

def points2img(fname):
    with open(fname) as f:
        for a in f:
            print(a)

