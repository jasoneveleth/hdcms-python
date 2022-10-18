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

# example: regex2stats1d(r"CM1_2_\d.txt", dir="../data")

