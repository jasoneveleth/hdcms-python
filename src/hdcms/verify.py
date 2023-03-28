def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

def assert_all_floats(l):
    for ele in l:
        if not isfloat(ele):
            raise RuntimeError(f"found: nonfloat {ele}")

def ms_valid_data_format(path_name):
    with open(path_name) as f:
        line_iter = iter(f.readlines())

        line = None

        # process header
        for line in line_iter:
            if line[0] != '#':
                break

        if not line:
            raise RuntimeError(f"empty file")

        fields = line.split(' \t,')
        assert_all_floats(fields)
        if len(fields) != 2:
            raise RuntimeError("got too many values per line")

        for line in line_iter:
            fields = line.split(' \t,')
            assert_all_floats(fields)
            if len(fields) != 2:
                raise RuntimeError("got too many values per line")


