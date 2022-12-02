# hdcms-helper

This library is available on pypi [here](https://pypi.org/project/hdcms-helper/). Install using `pip install hdcms-helper`.

How to use

```python
import hdcms_helper as hdc

hdc.generate_examples(visualize=True)
gaussian_sum_stat = hdc.regex2stats1d(r"gaus_\d+.txt")
laplacian_sum_stat = hdc.regex2stats1d(r"laplace_\d+\.txt")

# data in another directory for example:
# regex2stats2d(r"CM1_11_\d+.txt", dir="~/src/hdcms/data/")

print(hdc.compare(gaussian_sum_stat, laplacian_sum_stat))
hdc.write_image(gaussian_sum_stat, "tmp.png")
```

This library is built on top of the [`hdcms` package](https://pypi.org/project/hdcms/), which exposes python bindings to a C library. That bindings package contains only a few functions and lacks a nice user experience. But, if you are only interested in that, check it out.

You can see a complete list of functions (and where they are located) by running the following code. Look at the output of `help(hdc)` to get the right filename.

```python
import hdcms_helper as hdc
help(hdc)
with open(<filename>, 'r') as f:
    print(f.read())

help(hdc.regex2stats1d)
```

## Dependencies

Numpy is a necessary dependency for everything. Matplotlib and scipy are needed for `generate_example()`. opencv is required for `write_image()`.

## TODO

filter function for 2d spectra to filter out peaks with large x variation

## Change Log

0.1.8 Add documentation
