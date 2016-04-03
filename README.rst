memory-tools
========================

A set of simple yet effective tools to troubleshoot memory leaks.

Quick Start Tutorial
====================

Installation::

    $ pip install memory-tools

Show system memory::

    $ show-mem

    Commit Mem (MB):       27,852.80 total   17,278.42 used
    Physical Mem (MB):     16,384.00 total   13,128.05 used

With delta from last run::

    $ show-mem

    Commit Mem (MB):       27,852.80 total   17,888.59 used (delta: 310.15)
    Physical Mem (MB):     16,384.00 total   13,126.40 used (delta: -1.65)

Show memory for process::

    $ show-mem -p python

    1 process matching "python":
      PID 26143 (MB):           4.79 rss          1.23 private

    $ show-mem -p 26143

      PID 26143 (MB):           4.80 rss          1.24 private

Watch system/process memory using watch_::

    $ watch show-mem -s -p python

    Commit Mem (MB):       27,852.80 total   17,888.59 used (delta: 310.15)
    Physical Mem (MB):     16,384.00 total   13,126.40 used (delta: -1.65)

    2 processes matching "python" (showing 1st & last):
      PID 26143 (MB):          40.79 rss         30.23 private
      PID 24118 (MB):           4.79 rss          1.23 private


Links & Contact Info
====================

| Documentation: http://memory-tools.readthedocs.org
|
| PyPI Package: https://pypi.python.org/pypi/memory-tools
| GitHub Source: https://github.com/maxzheng/memory-tools
| Report Issues/Bugs: https://github.com/maxzheng/memory-tools/issues
|
| Connect: https://www.linkedin.com/in/maxzheng
| Contact: maxzheng.os @t gmail.com

.. _watch: https://en.wikipedia.org/wiki/Watch_(Unix)
