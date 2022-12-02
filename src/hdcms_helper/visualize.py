# https://stackoverflow.com/questions/49829783/draw-a-gradual-change-ellipse-in-skimage

import cv2
import numpy as np
import math

xpixels, ypixels = (1200, 400)

# proportion of screen dedicated as border
YBORDER = 0.1
XBORDER = 1.2 * (ypixels*YBORDER) / xpixels

# how much to scale the stddev
STD_SCALE = 1
# how much to add to the stddev after scale
# FAKE_NOISE = 3e-3
FAKE_NOISE = 1e-5

# thickness of axes
THICCNESS = 1

# width of 1d bin
BIN_WIDTH = 0.1
NUM_BINS = math.floor(900. / BIN_WIDTH)
WIDTH = 900. / NUM_BINS

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
    # Generate (x,y) coordinate arrays
    y,_ = np.mgrid[-k:height-k,-h:width-h] 
    # returns an array [[[-k, -k+1, ..., height-k-1, height-k], ...], 
    #                   [[-k, ..., -k], ..., [height-k, ..., height-k]]]

    weights = np.exp((-1/2) * ((y / ystd)**2))

    mask = np.zeros((height, width))
    lowest_x_rendered = int(h - (xwidth/2))
    highest_x_rendered = int(h + (xwidth/2))
    mask[:, lowest_x_rendered:highest_x_rendered] = 1

    weights *= mask
    if np.max(weights):
        return weights / np.max(weights)
    else:
        return weights

# overall goal: helper function when trying to convert (x,y) to pixel values of an image of size xpixels x ypixels with a border (of size XBORDER and YBORDER)
# coords are x from 0 to ~150, y from 0 to 1.0
# we want x_res and y_res to be the pixel values but from 0 to xwidth_noborder by 0 to ywidth_noborder
def scaling2pix(x,y,bounds): 
    min_x, min_y, max_x, max_y = bounds

    # the number of units in pre-transform image
    pre_xwidth = max_x - min_x
    pre_ywidth = max_y - min_y

    # number of pixels after the transform in the image in the x direction (if we subtract off the border pixels)
    post_xwidth_noborder = xpixels*(1 - 2 * XBORDER) 

    # number of pixels after the transform in the image in the y direction (if we subtract off the border pixels)
    post_ywidth_noborder = ypixels*(1 - 2 * YBORDER)

    x_res = post_xwidth_noborder * (x / pre_xwidth)
    y_res = post_ywidth_noborder * (y / pre_ywidth)
    return (x_res, y_res)

# overall goal: helper function when trying to convert (x,y) to pixel values of an image of size xpixels x ypixels with a border (of size XBORDER and YBORDER)
# coords are x from 0 to ~150, y from 0 to 1.0
# we want x_res and y_res to be the pixel values but from 0 to xpixels by 0 to ypixels, with the border
# and we need to flip the y values
def coords2pix(x,y,bounds): 
    x_res = (xpixels*XBORDER) + scaling2pix(x, y, bounds)[0]
    y_res = ypixels - (ypixels*YBORDER + scaling2pix(x,y, bounds)[1])
    return (x_res, y_res)

def write_image(data, filename):
    data = np.array(data)
    if len(data[0]) == 4:
        data[:,2] = data[:,2] * STD_SCALE + FAKE_NOISE
        data[:,3] = data[:,3] * STD_SCALE + FAKE_NOISE
    elif len(data[0]) == 2:
        data[:,1] = data[:,1] * STD_SCALE + FAKE_NOISE
    else:
        raise RuntimeError(f"Incorrect dimension: recieved {data.shape} must be nx2 or nx4")

    if len(data[0]) == 4:
        # min_x, min_y, max_x, max_y
        bounds = (0, 0, np.max(data[:, 0]), np.max(data[:, 1]))
    else:
        # min_x, min_y, max_x, max_y
        bounds = (0, 0, np.max(np.nonzero(data[:, 0])) * WIDTH, np.max(data[:, 0]))
    if len(data[0]) == 4:
        assert(np.min(data[:, 1]) >= 0 and np.min(data[:,0]) >= 0)

    img = np.zeros((ypixels, xpixels))

    for i, peak in enumerate(data):
        if len(peak) == 4:
            a, b = scaling2pix(peak[2], peak[3], bounds) # standard deviations
            h, k = coords2pix(peak[0], peak[1], bounds)
            img += gaussian_2d(xpixels, ypixels, h, k, a, b)
        else:
            if np.sum(peak) != 0.:
                width, sd = scaling2pix(WIDTH, peak[1], bounds) # width and standard deviations
                h, k = coords2pix(i * WIDTH, peak[0], bounds)
                img += gaussian_1d(xpixels, ypixels, h, k, sd, width)

    img = dress_image(img, bounds)

    cv2.imwrite(filename, img)

# this function is supposed to take the straight output of the gaussians and add axes, tickmarks, text
def dress_image(img, bounds):
    # invert -> most of image is ~1, and peaks are ~0
    img = np.clip(1 - img, 0, 1)

    # convert to B, G, R image rather than just single channel black and white
    one = np.ones(img.shape)
    img = cv2.merge((img, img, one)) # causes red to fill in peak areas

    # convert to bytes 0..1 -> 0..255
    img = np.uint8(img * 255)

    # xaxis
    cv2.line(img, (0, int(ypixels*(1-YBORDER))), (xpixels, int(ypixels*(1-YBORDER))), color=(0, 0, 0), thickness=THICCNESS)
    # yaxis
    cv2.line(img, (int(xpixels*XBORDER), 0), (int(xpixels*XBORDER), ypixels), color=(0, 0, 0), thickness=THICCNESS)

    max_x, max_y = bounds[2], bounds[3]

    # x-axis tick mark
    tick_x, tick_y = coords2pix(max_x, 0, bounds)
    tick_len = (ypixels * YBORDER / 5)
    # tick
    cv2.line(img, (int(tick_x), int(tick_y)), (int(tick_x), int(tick_y + tick_len)), color=(0,0,0))
    font = cv2.FONT_HERSHEY_PLAIN
    # label
    cv2.putText(img, str(int(max_x*10) / 10), (int(tick_x - 3 * tick_len), int(tick_y + 3.5 * tick_len)), fontFace=font, fontScale=1, color=(0,0,0))

    # y-axis tick mark
    tick_x, tick_y = coords2pix(0, max_y, bounds)
    tick_len = (ypixels * YBORDER / 5)
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

# example
# filename = "low_res.png" if len(sys.argv) < 2 else sys.argv[1]
# write_image(low_res, filename)

# filename = "high_res.png" if len(sys.argv) < 3 else sys.argv[2]
# write_image(high_res_data, filename)

