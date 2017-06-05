import gc
import locale
import logging
import os
import signal
import sys
import traceback

locale.setlocale(locale.LC_ALL, '')
log = logging.getLogger(__name__)


def fmt(stat):
    return locale.format('%d', stat, grouping=True)


def add_debug_handler(sig=signal.SIGUSR2, log_stack=True, start_debugger_password=None):
    """
      Add a signal handler for debugging by logging a stack or starting rpdb2 debugger.

      :param sig: Signal to attach handler to. Defaults to signal.SIGUSR2
      :param bool log_stack: Log stacktrace when the signal is received. Useful to find where the program is stuck.
      :param str start_debugger_password: Password to start rpdb2 debugger. By default, this is not started / only starts if
                                          a password is provided. Note that this depends on `rpdb2` module in `winpdb` package.
    """

    def debug_handler(_, frame):
        if log_stack:
            log.info("Got SIGUSR2. Traceback:\n%s", ''.join(traceback.format_stack(frame)))

        if start_debugger_password:
            try:
                import rpdb2
                rpdb2.start_embedded_debugger(start_debugger_password)
            except ImportError:
                log.error('rpdb2, part of winpdb, is required to start debugger. Please install package: pip install winpdb')

    signal.signal(sig, debug_handler)


def save_objects(objs=None):
    """
      Save gc.get_objects() to /var/tmp/objects-$pid with summary on top,
      from `summarize_objects`.

      Each object is converted to str and saved in descending order by size. I.e.::

        IDX 3648: 12568 <type 'dict'> {'REPEAT_ONE': 'repeat_one', 'makedict': <function makedict ...

      The above means array index 3648, 12568 bytes, data type dict, and data content as str.
      Easily go to the next record by searching for 'IDX '.

      :param list objs: gc objects to summarize. Defaults to gc.get_objects()
    """
    if not objs:
        gc.collect()
        objs = gc.get_objects()

    objs_sizes = sorted([(sys.getsizeof(o), i) for i, o in enumerate(objs)], reverse=True)
    objs_size = sum([s[0] for s in objs_sizes])
    objs_file = '/var/tmp/objects-%s' % os.getpid()

    with open(objs_file, 'w') as fp:
        fp.write('Objects count: %s\n' % fmt(len(objs)))
        fp.write('Objects size: %s\n\n' % fmt(objs_size))

        fp.write('Objects summary:\n%s\n\n' % summarize_objects(objs, echo=False, limit=20))

        for size, i in objs_sizes:
            try:
                fp.write('IDX %d: %d %s %s\n' % (i, size, type(objs[i]), str(objs[i])))
            except Exception as e:
                fp.write('IDX %d: %d %s EXCEPTION: %s\n' % (i, size, type(objs[i]), str(e)))

    msg = 'Wrote %d objects to %s (%d bytes)' % (len(objs), objs_file, objs_size)
    print(msg)

    return msg


def summarize_objects(objs=None, echo=True, limit=10):
    """
      Provide a summary of gc objects based on type. Two summaries: ordered by size, ordered by count

      :param list objs: gc objects to summarize. Defaults to gc.get_objects()
      :param bool echo: Print summary results to stdout if True, otherwise return results instead.
      :param int limit: Limit number of results in each summary. Defaults to show top 10.
      :return: Summary results if echo is False
    """
    if not objs:
        gc.collect()
        objs = gc.get_objects()

    objs_dict = _summarize_objects(objs)
    size_summary = ['{0:>10s} {1:>5s} {2}'.format('Size', 'Count', 'Type')]
    count_summary = ['{0:>5s} {1:>10s} {2}'.format('Count', 'Size', 'Type')]
    objs_by_size = []
    objs_by_count = []

    total_size = total_count = 0

    # Avoid importing six for this one issue
    iteritems = objs_dict.iteritems if hasattr(objs_dict, 'iteritems') else objs_dict.items

    for kind, stats in iteritems():
        objs_by_size.append((stats['size'], stats['count'], kind))
        objs_by_count.append((stats['count'], stats['size'], kind))
        total_size += stats['size']
        total_count += stats['count']

    for size, count, kind in sorted(objs_by_size, reverse=True):
        size_summary.append('{0:>10s} {1:>5s} {2}'.format(fmt(size), fmt(count), kind))

    for count, size, kind in sorted(objs_by_count, reverse=True):
        count_summary.append('{0:>5s} {1:>10s} {2}'.format(fmt(count), fmt(size), kind))

    if echo:
        print('Objects count', fmt(total_count))
        print('Objects size', fmt(total_size))
        print()

        for summary in [size_summary, count_summary]:
            print('\n'.join(summary[:limit + 1]))
            if len(summary) > 10:
                print('... %d more' % (len(summary) - limit - 1))
            print()

    else:
        return '\n'.join(size_summary + [''] + count_summary)


def _summarize_objects(objs):
    objs_dict = {}

    for obj in objs:
        _incr(objs_dict, type(obj), 'count')
        _incr(objs_dict, type(obj), 'size', sys.getsizeof(obj))

    return objs_dict


def _incr(objs_dict, kind, stat, value=1):
    if kind not in objs_dict:
        objs_dict[kind] = {}

    if stat not in objs_dict[kind]:
        objs_dict[kind][stat] = value
    else:
        objs_dict[kind][stat] += value
