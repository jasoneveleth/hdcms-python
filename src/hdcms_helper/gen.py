import scipy.stats
import numpy as np
from matplotlib import pyplot as plt

SCALE_RADIUS = 0.01
ADD_RADIUS = 0.001
MEAN = 200
N = 100

def data(dist):
    """create data"""
    sample = dist.rvs(size=(N, 2), loc=MEAN) # we get garbage for y values
    sample[:,1] = dist.pdf(sample[:,0], loc=MEAN)
    return smear(sample)

def plot(data, title="no title provided"):
    """plot data on a graph"""
    plt.scatter(data[:,0], data[:,1])
    plt.title(title)
    plt.xlim(190, 210)
    plt.ylim(0,0.6)
    plt.show()

def smear(data):
    """add noise to data"""
    scale = 1 + np.random.random() * SCALE_RADIUS - SCALE_RADIUS
    add = np.random.random() * ADD_RADIUS - ADD_RADIUS
    data[:,1] *= scale
    data[:,1] += add
    return data

def generate_examples(visualize=False):
    """use scipy statistics distributions to generate synthetic data"""
    for i in range(10):
        with open(f"gaus_{i}.txt", "w") as f:
            d = data(scipy.stats.norm)
            for pt in d:
                print(pt[0], pt[1], file=f)
            if visualize:
                plot(d, "gaussian")

    for i in range(10):
        with open(f"laplace_{i}.txt", "w") as f:
            d = data(scipy.stats.laplace)
            for pt in d:
                print(pt[0], pt[1], file=f)
            if visualize:
                plot(d, "laplace")

    for i in range(10):
        with open(f"cauchy_{i}.txt", "w") as f:
            d = data(scipy.stats.cauchy)
            for pt in d:
                print(pt[0], pt[1], file=f)
            if visualize:
                plot(d, "cauchy")

    for i in range(3):
        with open(f"unknown_{i}.txt", "w") as f:
            d = data(scipy.stats.laplace)
            for pt in d:
                print(pt[0], pt[1], file=f)
            if visualize:
                plot(d, "unknown (laplace)")

    with open("params.txt", "w") as f:
        print("Parameters when we last ran `gen.py`:", file=f)
        print(f"SCALE_RADIUS: {SCALE_RADIUS}", file=f)
        print(f"ADD_RADIUS: {ADD_RADIUS}", file=f)
        print(f"MEAN: {MEAN}", file=f)
        print(f"N: {N}", file=f)

