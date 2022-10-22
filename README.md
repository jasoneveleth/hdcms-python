# hdcms-helper

How to use

```python
import hdcms_helper as hdc

hdc.generate_examples()
gaussian_sum_stat = hdc.regex2stats1d(r"gaus_\d+.txt")
laplacian_sum_stat = hdc.regex2stats1d(r"laplace_\d+\.txt")

# data in another directory for example:
# regex2stats2d(r"CM1_11_\d+.txt", dir="~/src/hdcms/data/")

print(hdc.compare(gaussian_sum_stat, laplacian_sum_stat))
hdc.write_image(gaussian_sum_stat, "tmp.png")
```

