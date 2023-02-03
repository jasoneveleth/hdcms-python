# hdcms

This library is available on pypi [here](https://pypi.org/project/hdcms/). Install using `pip install hdcms`.

How to use

```python
import hdcms as hdc

hdc.generate_examples(visualize=True)
gaussian_sum_stat = hdc.regex2stats1d(r"gaus_\d+.txt")
laplacian_sum_stat = hdc.regex2stats1d(r"laplace_\d+\.txt")

# data in another directory for example:
# regex2stats2d(r"CM1_11_\d+.txt", dir="~/src/hdcms/data/")

print(hdc.compare(gaussian_sum_stat, laplacian_sum_stat))
hdc.write_image(gaussian_sum_stat, "tmp.png")
```

This library is built on top of the [`hdcms-bindings` package](https://pypi.org/project/hdcms-bindings/), which exposes python bindings to a C library. That bindings package contains only a few functions and lacks a nice user experience. But, if you are only interested in that, check it out.

# Summary of provided functions

`regex2stats1d`, `regex2stats2d` - takes regex and converts to summary statistic
`array2stats1d`, `array2stats2d` - takes a varargs list of numpy arrays and converts them into 1d summary statistic
`file2stats1d`, `file2stats2d` - takes filename and converts it to a summary stat. it is expected that the file contents are a list of filenames on separate lines
`filenames2stats1d`, `filenames2stats2d` - takes list of filenames and converts it to a summary stat
`compare` - compares two summary statistics
`write_image` - visualizes a summary statistic
`clean` - takes list of filenames and shows you what changes need to be made
`generate_examples` - generate synthetic data as an example

## Dependencies

Numpy is a necessary dependency for every function. 
Matplotlib and scipy are needed for \verb|generate_example()|, which will generate a raondom synthetic data set. 
opencv is required for \verb|write_image()|, which will visualize summary statistics. 
You can see a complete list of functions (and where they are located) by running the following code.
Look at the output of \verb|help(hdc)| to get the right filename.

## TODO

filter function for 2d spectra to filter out peaks with large x variation

## Change Log

0.1.12 Add params to write_image
0.1.11 Fix problems introduced by rename
0.1.10 Really rename (broken)
0.1.9 Rename, performance for visulize in 1D case (broken)
0.1.8 Add documentation
