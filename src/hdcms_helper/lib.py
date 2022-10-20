import hdcms
import re
import os

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

# TODO: numpy arrays to stats
