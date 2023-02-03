# https://stackoverflow.com/questions/49829783/draw-a-gradual-change-ellipse-in-skimage

import cv2
import numpy as np
import math
import sys

class ImageConfig:
    # designed to be called by write(), so it's very coupled
    def __init__(self, xpixels, ypixels, yborder, xborder, std_scale, fake_noise, thickness, bin_width, num_bins, width):
        self.xpixels = xpixels
        self.ypixels = ypixels

        # proportion of screen dedicated as border
        self.yborder = yborder
        self.xborder = xborder or (1.2 * (self.ypixels*self.yborder) / self.xpixels)

        # how much to scale the stddev
        self.std_scale = std_scale
        # how much to add to the stddev after scale
        self.fake_noise = fake_noise

        # thickness of axes
        self.thickness = thickness

        # width of 1d bin
        self.bin_width = bin_width
        self.num_bins = num_bins or math.floor(900. / self.bin_width)
        self.width = width or 900. / self.num_bins

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

def gaussian_1d(width, height, h, k, ystd, xwidth):
    lowest_x_rendered = int(h - (xwidth/2))
    highest_x_rendered = int(h + (xwidth/2))
    if lowest_x_rendered == highest_x_rendered:
        print(f"pixel width of {(h,k)} in image of size {(width, height)} (width, height), with ystd: {ystd}, xwidth: {xwidth}", file=sys.stderr)
        return np.zeros((height, width))
    y,_ = np.mgrid[-k:height-k, lowest_x_rendered:highest_x_rendered]
    # so sets y to [[-k, -k, -k, ..., -k, -k],
    #               [-(k-1), -(k-1), -(k-1), ..., -(k-1)],
    #               ...
    #               [(height-k-1), (height-k-1), ..., (height-k-1)]]
    # with the number of columns equal to (highest_x_rendered - lowest_x_rendered)
    weights = np.exp((-1/2) * ((y / ystd)**2))

    ret = np.zeros((height, width))
    ret[:, lowest_x_rendered:highest_x_rendered] = weights
    if weights.size != 0 and np.max(weights) != 0:
        return ret / np.max(weights)
    else:
        return ret

# overall goal: helper function when trying to convert (x,y) to pixel values of an image of size xpixels x ypixels with a border (of size XBORDER and YBORDER)
# coords are x from 0 to ~150, y from 0 to 1.0
# we want x_res and y_res to be the pixel values but from 0 to xwidth_noborder by 0 to ywidth_noborder
def scaling2pix(x, y, bounds, config): 
    min_x, min_y, max_x, max_y = bounds

    # the number of units in pre-transform image
    pre_xwidth = max_x - min_x
    pre_ywidth = max_y - min_y

    # number of pixels after the transform in the image in the x direction (if we subtract off the border pixels)
    post_xwidth_noborder = config.xpixels*(1 - 2 * config.xborder) 

    # number of pixels after the transform in the image in the y direction (if we subtract off the border pixels)
    post_ywidth_noborder = config.ypixels*(1 - 2 * config.yborder)

    x_res = post_xwidth_noborder * (x / pre_xwidth)
    y_res = post_ywidth_noborder * (y / pre_ywidth)
    return (x_res, y_res)

# overall goal: helper function when trying to convert (x,y) to pixel values of an image of size xpixels x ypixels with a border (of size XBORDER and YBORDER)
# coords are x from 0 to ~150, y from 0 to 1.0
# we want x_res and y_res to be the pixel values but from 0 to xpixels by 0 to ypixels, with the border
# and we need to flip the y values
def coords2pix(x, y, bounds, config): 
    x_res = (config.xpixels*config.xborder) + scaling2pix(x, y, bounds, config)[0]
    y_res = config.ypixels - (config.ypixels*config.yborder + scaling2pix(x,y, bounds, config)[1])
    return (x_res, y_res)

def write_image(data, filename, xpixels=3600, ypixels=1200, yborder=0.1, xborder=None, std_scale=1, fake_noise=1e-5, thickness=1, bin_width=0.1, num_bins=None, width=None):
    config = ImageConfig(xpixels, ypixels, yborder, xborder, std_scale, fake_noise, thickness, bin_width, num_bins, width)

    data = np.array(data)
    if len(data[0]) == 4:
        data[:,2] = data[:,2] * config.std_scale + config.fake_noise
        data[:,3] = data[:,3] * config.std_scale + config.fake_noise
    elif len(data[0]) == 2:
        data[:,1] = data[:,1] * config.std_scale + config.fake_noise
    else:
        raise RuntimeError(f"Incorrect dimension: recieved {data.shape} must be nx2 or nx4")

    if len(data[0]) == 4:
        # min_x, min_y, max_x, max_y
        bounds = (0, 0, np.max(data[:, 0]), np.max(data[:, 1]))
    else:
        # min_x, min_y, max_x, max_y
        bounds = (0, 0, np.max(np.nonzero(data[:, 0])) * config.width, np.max(data[:, 0]))
    if len(data[0]) == 4:
        assert(np.min(data[:, 1]) >= 0 and np.min(data[:,0]) >= 0)

    img = np.zeros((ypixels, xpixels))

    for i, peak in enumerate(data):
        if len(peak) == 4:
            a, b = scaling2pix(peak[2], peak[3], bounds, config) # standard deviations
            h, k = coords2pix(peak[0], peak[1], bounds, config)
            img += gaussian_2d(xpixels, ypixels, h, k, a, b)
        else:
            if np.sum(peak[0]) != 0.:
                width, sd = scaling2pix(config.width, peak[1], bounds, config) # width and standard deviations
                h, k = coords2pix(i * config.width, peak[0], bounds, config)
                img += gaussian_1d(xpixels, ypixels, h, k, sd, width)

    img = dress_image(img, bounds, config)

    cv2.imwrite(filename, img)

# this function is supposed to take the straight output of the gaussians and add axes, tickmarks, text
def dress_image(img, bounds, config):
    # invert -> most of image is ~1, and peaks are ~0
    img = np.clip(1 - img, 0, 1)

    # convert to B, G, R image rather than just single channel black and white
    one = np.ones(img.shape)
    img = cv2.merge((img, img, one)) # causes red to fill in peak areas

    # convert to bytes 0..1 -> 0..255
    img = np.uint8(img * 255)

    # xaxis
    cv2.line(img, (0, int(config.ypixels*(1-config.yborder))), (config.xpixels, int(config.ypixels*(1-config.yborder))), color=(0, 0, 0), thickness=config.thickness)
    # yaxis
    cv2.line(img, (int(config.xpixels*config.xborder), 0), (int(config.xpixels*config.xborder), config.ypixels), color=(0, 0, 0), thickness=config.thickness)

    max_x, max_y = bounds[2], bounds[3]

    # x-axis tick mark
    tick_x, tick_y = coords2pix(max_x, 0, bounds, config)
    tick_len = (config.ypixels * config.yborder / 5)
    # tick
    cv2.line(img, (int(tick_x), int(tick_y)), (int(tick_x), int(tick_y + tick_len)), color=(0,0,0))
    font = cv2.FONT_HERSHEY_PLAIN
    # label
    cv2.putText(img, str(int(max_x*10) / 10), (int(tick_x - 3 * tick_len), int(tick_y + 3.5 * tick_len)), fontFace=font, fontScale=1, color=(0,0,0))

    # y-axis tick mark
    tick_x, tick_y = coords2pix(0, max_y, bounds, config)
    tick_len = (config.ypixels * config.yborder / 5)
    # tick
    cv2.line(img, (int(tick_x - tick_len), int(tick_y)), (int(tick_x), int(tick_y)), color=(0,0,0))
    font = cv2.FONT_HERSHEY_PLAIN
    # label
    cv2.putText(img, str(int(max_y*100) / 100), (int(tick_x - 5 * tick_len), int(tick_y)), fontFace=font, fontScale=1, color=(0,0,0))
    return img

def points2img(fname):
    with open(fname) as f:
        for a in f:
            print(a)

