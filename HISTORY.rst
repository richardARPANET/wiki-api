.. :changelog:

Release History
---------------

2.0.0 (2020-09-15)
++++++++++++++++++

- Drops Python 2 support.
- Adds ``get_tables`` method to get all tables of data from a given Wikipedia page.


1.2.5 (2016-07-09)
++++++++++++++++++

- Fixes bug in caching with Python 3


1.2.4 (2015-07-26)
++++++++++++++++++

- Fixes bug with cache keys not being unique, leading to incorrect response coming from cache (see ISSUE #9)


1.2.3 (2015-07-21)
++++++++++++++++++

- Adds logging of find() response from Wikipedia


1.2.2 (2015-06-08)
++++++++++++++++++

**Bugfixes**

- Fixes missing dependency in install_requires


1.2.1 (2015-06-08)
++++++++++++++++++

**Bugfixes**

- Fixes missing "double quotes" in Article.summary


1.2.0 (2015-05-16)
++++++++++++++++++

**Changed**

- ``Article.content`` now will not contain sentences including Wikipedia ad lines.

1.1.2 (2014-12-25)
++++++++++++++++++

- No notes, release made before changelog inception.
