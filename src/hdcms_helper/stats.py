import hdcms
import re
import os
import sys
import numpy as np
from hdcms import filenames_to_stats_1d as filenames2stats1d
from hdcms import filenames_to_stats_2d as filenames2stats2d

def regex2filenames(regex, dir="."):
    files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]

    r = re.compile(regex)
    a = []
    for f in files:
        match = r.match(f)
        if match:
            a.append(match.group())

    full_paths = list(map(lambda f: os.path.join(dir, f), a))
    return ','.join(full_paths)

def regex2stats1d(regex, dir="."):
    filenames = regex2filenames(regex, dir)
    return hdcms.filenames_to_stats_1d(filenames)

def regex2stats2d(regex, dir="."):
    filenames = regex2filenames(regex, dir)
    return hdcms.filenames_to_stats_2d(filenames)

# example: regex2stats1d(r"CM1_2_\d.txt", dir="../data")

def file2filenames(filename):
    with open(filename) as f:
        return ",".join(f.readlines())

def file2stats1d(filename):
    return hdcms.filenames_to_stats_1d(file2filenames(filename))

def file2stats2d(filename):
    return hdcms.filenames_to_stats_2d(file2filenames(filename))

# example: file2stats2d("./compound1_high_res.txt")

def get_unique_tmpdir(name="hdcms-numpy-tmp"):
    dir = f"/tmp" if sys.platform != "win32" else f"C:\\Users\\AppData\\Local\\Temp"
    _, existing_dirs, _ = next(os.walk(dir))
    while name in existing_dirs:
        name += "0"
    return os.path.join(dir, name)

def array2stats1d(*args):
    dir = get_unique_tmpdir()
    lst = []
    for i, arr in args:
        filename = os.path.join(dir, f"{i}-numpy-array.txt")
        np.savetxt(filename, arr)
        lst.append(filename)
    return hdcms.filenames_to_stats_1d(",".join(lst))

def array2stats2d(*args):
    dir = get_unique_tmpdir()
    lst = []
    for i, arr in args:
        filename = os.path.join(dir, f"{i}-numpy-array.txt")
        np.savetxt(filename, arr)
        lst.append(filename)
    return hdcms.filenames_to_stats_2d(",".join(lst))

# figures out the comparison function needed and checks that the input is valid size
def compare(*args, npeaks=None):
    is_using_2d = (npeaks != None)
    if len(args) == 1:
        raise RuntimeError("Must compare at least 2 summary statistics")

    # verify they all have the same length of second dimension
    len_of_dim_2 = args[0].shape[1]
    for arr in args:
        if arr.shape[1] != len_of_dim_2:
            raise RuntimeError(f"Mismatch dimension: recieved {arr.shape} and {args[0].shape}, they must be the same and either (_, 2) or (_, 4)")

    # make sure it is either 2 or 4
    if len_of_dim_2 not in [2,4]:
        raise RuntimeError(f"Incorrect dimension: recieved {args[0].shape} must be (_, 2) or (_, 4)")

    # make sure they are using the right number of peaks
    if len_of_dim_2 == 2 and is_using_2d:
        raise RuntimeError("Mismatch dimension: supplied npeaks={npeaks} but using an array with dimensions {args[0].shape}. To use 2d comparison must be (_, 4)")

    if len(args) == 2:
        if is_using_2d:
            return hdcms.compare_compound_2d(args[0], args[1])
        else:
            return hdcms.compare_compound_1d(args[0], args[1])
    else:
        if is_using_2d:
            return hdcms.compare_all_2d(args)
        else:
            return hdcms.compare_all_1d(args)
