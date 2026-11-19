# News citation address audit

Both chunkers processed the same immutable canonical news texts. An ambiguous original identifier points to multiple distinct passages. Every offset-indexed slice is compared with its source bytes after UTF-8 decoding.

| Files | Original spans | Ambiguous line IDs | Affected files | Offset spans | Duplicate offset IDs | Incorrect slices |
| --- | --- | --- | --- | --- | --- | --- |
| 609 | 6420 | 5 | 1 | 6220 | 0 | 0 |
