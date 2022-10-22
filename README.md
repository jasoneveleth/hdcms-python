# hdcms-helper

How to use

```python
import hdcms_helper.lib as pyhdcms
from hdcms_helper.lib import regex2stats2d
from hdcms_helper.visualize import write_image

pyhdcms.regex2stats1d(r"CM1_11_\d+.txt", dir="~/src/hdcms/data/")
summary = regex2stats2d(r"CM1_11_\d+.txt", dir="~/src/hdcms/data/")
write_image(summary, "tmp.png")
```

    gaussian = regex2stats1d(r'gaus_\d+\.txt')
    laplace = regex2stats1d(r'laplace_\d+\.txt')
    cauchy = regex2stats1d(r'cauchy_\d+\.txt')
    unknown = regex2stats1d(r'unknown_\d+\.txt')
    print(hdcms.compare_all_1d([gaussian, laplace, cauchy]))
    print(hdcms.compare_compound_1d(unknown, gaussian))
    print(hdcms.compare_compound_1d(unknown, cauchy))
    print(hdcms.compare_compound_1d(unknown, laplace))

