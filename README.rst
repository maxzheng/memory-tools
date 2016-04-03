memory-tools
========================

A set of simple yet effective tools to troubleshoot memory leaks.

Quick Start Tutorial
====================

Installation::

    $ pip install memory-tools

Show system memory:

    $ show-mem

    Physical Mem (MB):     16,384.00 total   13,128.05 used

With delta from last run:

    $ show-mem

    Physical Mem (MB):     16,384.00 total   13,126.40 used (delta: -1.65)

Show memory for process:

    $ show-mem -p Python

    1 process matching "python":
      PID 26143 (MB):           4.79 rss          1.23 private


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
