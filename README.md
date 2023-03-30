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

This library is built on top of the [`hdcms-bindings` package](https://pypi.org/project/hdcms-bindings/), which exposes python bindings to a C library. That bindings package contains only a few functions and lacks a nice user experience. But, if you are only interested in that, check it out.

For more documentation: see [`examples/` directory](https://github.com/jasoneveleth/hdcms-python/tree/main/examples).

## Dependencies

`numpy` is a necessary dependency for every function. 

`matplotlib` and scipy are needed for `generate_example()`, which will generate a random synthetic data set. 

opencv is required for `write_image()`, which will visualize summary statistics. 


## Change Log

```
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
