import hdcms
import re
import os
import sys
import numpy as np

def file_ok(fname):
    """ensure that fname is a file"""
    if not (os.path.isfile(fname) and os.access(fname, os.R_OK)):
        raise RuntimeError(f"File {fname} doesn't exist or isn't readable")

def filenames2stats1d(filenames):
    """take filenames and convert them into a 1d summary statistic"""
    for f in filenames.split(","):
        file_ok(f)
    return hdcms.filenames_to_stats_1d(filenames)

def filenames2stats2d(filenames):
    """take filenames and convert them into a 2d summary statistic"""
    for f in filenames.split(","):
        if not (os.path.isfile(f) and os.access(f, os.R_OK)):
            raise RuntimeError(f"File {f} doesn't exist or isn't readable")
    return hdcms.filenames_to_stats_2d(filenames)

def regex2filenames(regex, dir="."):
    """takes regex, finds all files that match and convert them into list of filenames"""
    files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]

    r = re.compile(regex)
    matches = []
    for f in files:
        match = r.match(f)
        if match:
            matches.append(match.group())

    if len(matches) == 0:
        raise RuntimeError(f"No matches for {regex} in directory {dir}")

    full_paths = list(map(lambda f: os.path.join(dir, f), matches))
    return ','.join(full_paths)

def regex2stats1d(regex, dir="."):
    """takes regex, converts list of filenames that match into 1d summary stat"""
    filenames = regex2filenames(regex, dir)
    return filenames2stats1d(filenames)

def regex2stats2d(regex, dir="."):
    """takes regex, converts list of filenames that match into 2d summary stat
       example: regex2stats1d(r"CM1_2_\d.txt", dir="../data")"""
    filenames = regex2filenames(regex, dir)
    return filenames2stats2d(filenames)

def file2filenames(filename):
    """takes file with filenames on separate lines and joins them into a string of filenames separated by commas"""
    with open(filename) as f:
        return ",".join(f.readlines())

def file2stats1d(filename):
    """takes file with filenames on separate lines converts them into a 1d summary statistic"""
    return filenames2stats1d(file2filenames(filename))

def file2stats2d(filename):
    """takes file with filenames on separate lines converts them into a 2d summary statistic
       example: file2stats2d("./compound1_high_res.txt")"""
    return filenames2stats2d(file2filenames(filename))

def get_unique_tmpdir(name="hdcms-numpy-tmp"):
    """creates a unique temporary directory, in unix it's /tmp, on windows its C:\Users\AppData\Local\Temp"""
    dir = f"/tmp" if sys.platform != "win32" else f"C:\\Users\\AppData\\Local\\Temp"
    _, existing_dirs, _ = next(os.walk(dir))
    while name in existing_dirs:
        name += "0"
    return os.path.join(dir, name)

def array2stats1d(*args):
    """takes a varargs list of numpy arrays and converts them into 1d summary statistic"""
    dir = get_unique_tmpdir()
    lst = []
    for i, arr in args:
        filename = os.path.join(dir, f"{i}-numpy-array.txt")
        np.savetxt(filename, arr)
        lst.append(filename)
    return filenames2stats1d(",".join(lst))

def array2stats2d(*args):
    """takes a varargs list of numpy arrays and converts them into 2d summary statistic"""
    dir = get_unique_tmpdir()
    lst = []
    for i, arr in args:
        filename = os.path.join(dir, f"{i}-numpy-array.txt")
        np.savetxt(filename, arr)
        lst.append(filename)
    return filenames2stats2d(",".join(lst))

# figures out the comparison function needed and checks that the input is valid size
def compare(*args, npeaks=None):
    """takes varargs list of summary statistic and computes the similarity according to its arguments,
       so if all arrays are 1d summary stats it will compare them using 1d similarity, same with 2d, if
       anything doesn't match it will raise a helpful error message"""
    is_using_2d = (npeaks != None)
    if len(args) <= 1:
        raise RuntimeError("Must compare at least 2 summary statistics")

    len_of_dim_2 = args[0].shape[1]

    # make sure it is either 2 or 4
    if len_of_dim_2 not in [2,4]:
        raise RuntimeError(f"Incorrect dimension: recieved {args[0].shape} must be (_, 2) or (_, 4)")

    # make sure they are using the right number of peaks
    if len_of_dim_2 == 2 and is_using_2d:
        raise RuntimeError("Mismatch dimension: supplied npeaks={npeaks} but using an array with dimensions {args[0].shape}. To use 2d comparison must be (_, 4)")
    elif len_of_dim_2 == 4:
        is_using_2d = True

    # verify they all have the same length of second dimension
    for arr in args:
        if arr.shape[1] != len_of_dim_2:
            raise RuntimeError(f"Mismatch dimension: recieved {arr.shape} and {args[0].shape}, they must be the same and either (_, 2) or (_, 4)")

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

