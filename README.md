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
