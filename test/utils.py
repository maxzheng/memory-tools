from contextlib import contextmanager
import shutil
from tempfile import mkdtemp


@contextmanager
def temp_directory():
    temp_dir = mkdtemp()

    try:
        yield temp_dir

    finally:
        shutil.rmtree(temp_dir)
