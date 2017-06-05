from collections import namedtuple
from memorytools.show_mem import main, KB, MB

from utils import temp_directory

def test_show_mem(runner, monkeypatch):
    MemStats = namedtuple('MemStats', ['total', 'used'])

    with temp_directory() as temp_dir:
        monkeypatch.setattr('tempfile.gettempdir', lambda: temp_dir)
        monkeypatch.setattr('psutil.virtual_memory', lambda: MemStats(100 * MB, 30 * MB))

        monkeypatch.setattr('memorytools.show_mem._get_meminfo',
                            lambda: 'CommitLimit:    {0} kB\nCommitted_AS:    {1} kB'.format(100 * KB, 70 * KB))

        result = runner.invoke(main)

        assert result.exit_code == 0
        assert result.output == 'Commit Mem (MB):          100.00 total       70.00 used \n' \
                                'Physical Mem (MB):        100.00 total       30.00 used \n'

        monkeypatch.setattr('psutil.virtual_memory', lambda: MemStats(100 * MB, 40 * MB))
        monkeypatch.setattr('memorytools.show_mem._get_meminfo',
                            lambda: 'CommitLimit:    {0} kB\nCommitted_AS:    {1} kB'.format(100 * KB, 90 * KB))

        result = runner.invoke(main)

        assert result.exit_code == 0
        assert result.output == 'Commit Mem (MB):          100.00 total       90.00 used (delta: 20.00)\n' \
                                'Physical Mem (MB):        100.00 total       40.00 used (delta: 10.00)\n'


def test_show_mem_process(runner, monkeypatch):
    MemStats = namedtuple('MemStats', ['rss'])

    with temp_directory() as temp_dir:
        monkeypatch.setattr('tempfile.gettempdir', lambda: temp_dir)
        monkeypatch.setattr('psutil.Process.memory_info', lambda pid: MemStats(30 * MB))
        monkeypatch.setattr('memorytools.show_mem._get_smaps',
                            lambda pid: 'Private_Clean:    {0} kB\nPrivate_Dirty:    {1} kB'.format(100 * KB, 90 * KB))

        result = runner.invoke(main, ['-p', '123'])

        assert result.exit_code == 0
        assert result.output == 'PID   123 (MB):            30.00 rss        190.00 private\n'
