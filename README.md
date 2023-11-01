# hdcms

This library is available on pypi [here](https://pypi.org/project/hdcms/). Install using `pip install hdcms`.

A very simple example:

```python
import hdcms as hdc

hdc.generate_examples(visualize=True)
gaussian_sum_stat = hdc.regex2stats1d(r"gaus_\d+.txt")
laplacian_sum_stat = hdc.regex2stats1d(r"laplace_\d+\.txt")

print(hdc.compare(gaussian_sum_stat, laplacian_sum_stat))
hdc.write_image(gaussian_sum_stat, "tmp.png")
```

For more documentation: see [`examples/` directory](https://github.com/jasoneveleth/hdcms-python/tree/main/examples).

## Dependencies

This library is built on top of the [`hdcms-bindings` package](https://pypi.org/project/hdcms-bindings/), which exposes python bindings to a C library. 

`numpy` is a necessary dependency for every function. 

`matplotlib` and scipy are needed for `generate_example()`, which will generate a random synthetic data set. 

## Change Log

```
0.1.27 version 0.1.27: updating rounding in gaussian2d code
0.1.26 Bug fix: npeaks for y-hdc for visualization was possible
0.1.25 Added missing optional args for filenames2stats*
0.1.24 Add npeaks for visualization
0.1.23 Add xtol
0.1.22 Fix new colors for write_image
0.1.21 New colors for write_image
0.1.20 Change name from ms_valid_data_format to is_valid_ms_data_format + scaling, start, end, num_bins
0.1.19 Return image from write_image
0.1.18 Add labels to visualization configuration options
0.1.17 Use matplotlib axes rather than my own
0.1.16 Bug fixes (text for x axis, names for regex2filenames)
0.1.15 Return image from write_image, rather than writing to file
0.1.14 Add new params to write_image
0.1.13 Add new params to write_image
0.1.12 Add params to write_image
0.1.11 Fix problems introduced by rename
0.1.10 Really rename (broken)
0.1.9 Rename, performance for visulize in 1D case (broken)
0.1.8 Add documentation
```
