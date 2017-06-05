#!/usr/bin/env python

import locale
import logging
import os
import tempfile

import click
import psutil

logging.basicConfig(level=logging.ERROR, format='[%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

KB = 1024
KB_NAME = 'kB'

MB = KB * KB
MB_NAME = 'MB'


@click.command()
@click.option('-p', '--process', metavar='name/id', help='Show memory usage of process with name/id.')
@click.option('-s', '--system', is_flag=True, help='Show system memory usage with delta. [default]')
@click.help_option('-h')
def main(process, system):
    if system or not(process):
        show_system_stats()

    if process:
        show_process_stats(process, prefer_break=system)


def f(num):
    return locale.format("%.2f", num, grouping=True)


def show_system_stats():
    show_commit_stats()
    show_physical_stats()


def show_process_stats(name_or_id, prefer_break=False):
    """
      :param str|int name_or_id: Process name or id to filter
      :param bool prefer_break: Add extra newline if needed
    """
    pids = []
    prefer_indent = False

    try:
        pids.append(int(name_or_id))

    except Exception:
        all_pids = []

        for process in psutil.process_iter():
            try:
                if name_or_id.lower() in process.name().lower():
                    all_pids.append(process.pid)
            except Exception as e:
                log.debug('Could not get name of process %s: %s', process, e)
                continue

        plural = ''
        first_and_last = ''

        if len(all_pids) == 1:
            pids = all_pids
        elif len(all_pids) > 1:
            pids = [all_pids[0], all_pids[-1]]
            plural = 'es'
            first_and_last = ' (showing 1st & last)'
        else:
            log.error('No process found matching "%s"', name_or_id)
            return

        prefer_indent = True
        if prefer_break:
            click.echo()

        click.echo('{3:d} process{0} matching "{1}"{2}:'.format(plural, name_or_id, first_and_last, len(all_pids)))

    for pid in pids:
        show_pid_stats(pid, prefer_indent=prefer_indent)


def show_pid_stats(pid, prefer_indent):
    try:
        process = psutil.Process(pid)
        mem = process.memory_info()
    except Exception as e:
        log.error('Could not get memory info for PID %d: %s', pid, e)
        return

    stats = [(mem.rss, 'rss')]

    private_mem = _get_private_mem(pid)
    if private_mem:
        stats.append((private_mem, 'private'))

    _show_mem_stats(
        title='{0}PID {1:5d}'.format('  ' if prefer_indent else '', pid),
        stats=stats)


def _get_private_mem(pid):
    total_private = 0

    smaps = _get_smaps(pid)

    if smaps:
        for line in smaps.split('\n'):
            if line.startswith('Private_'):
                name, amount, unit = line.split()

                if unit == KB_NAME:
                    total_private += int(amount) * KB
                elif unit == MB_NAME:
                    total_private += int(amount) * MB
                else:
                    raise Exception('Unsupported memory unit for Private_* memory info from /proc/%d/smaps', pid)

    return total_private


def _get_smaps(pid):
    try:
        with open('/proc/%d/smaps' % pid) as fp:
            return fp.read()
    except IOError as e:
        log.debug('Failed to parse /proc/%d/smaps: %s', pid, e)


def show_commit_stats():
    mem_info = _get_meminfo()

    if not mem_info:
        return

    total_commit = total_used = 0
    memory_unit = None

    for line in mem_info.split('\n'):
        if line.startswith('Commit'):
            mem_field, mem_value, memory_unit = line.split()

            if mem_field == 'CommitLimit:':
                total_commit = int(mem_value)

            elif mem_field == 'Committed_AS:':
                total_used = int(mem_value)

    if not (total_used and total_commit):
        log.error('Odd, did not find CommitLimit/Committed_AS in /proc/meminfo')
        return

    if memory_unit == KB_NAME:
        total_commit = total_commit * KB
        total_used = total_used * KB
    elif memory_unit == MB_NAME:
        total_commit = total_commit * MB
        total_used = total_used * MB
    else:
        log.error('Unsupported memory unit for Commit* memory info from /proc/meminfo')
        return

    _show_mem_stats_with_delta("Commit Mem", total_commit, total_used)


def show_physical_stats():
    vm_stats = psutil.virtual_memory()

    used = vm_stats.used

    if hasattr(vm_stats, 'buffers'):
        used -= vm_stats.buffers

    if hasattr(vm_stats, 'cached'):
        used -= vm_stats.cached

    _show_mem_stats_with_delta('Physical Mem', vm_stats.total, used)


def _show_mem_stats_with_delta(title, total, used):
    last_used = _last_used_mem(title, current_used=used)

    if last_used:
        delta = ' (delta: {0})'.format(f((used - last_used) / float(MB)))
    else:
        delta = ''

    _show_mem_stats(title, [
      (total, 'total'),
      (used, 'used{0}'.format(delta))])


def _show_mem_stats(title, stats):
    """
      :param str title:
      :param list(tuple) stats: I.e. [(bytes, name), ...]
    """
    formatted_stats = ['{0:20}'.format('{0} ({1}):'.format(title, MB_NAME))]

    for mem_bytes, name in stats:
        formatted_stats.append('{0:>10s} {1:5}'.format(f(mem_bytes / float(MB)), name))

    click.echo('  '.join(formatted_stats))


def _last_used_mem(name, current_used):
    used_mem_file = os.path.join(tempfile.gettempdir(), 'show-mem-' + name.replace(' ', '_'))

    try:
        with open(used_mem_file) as fp:
            last_used_str = fp.read()

            try:
                last_used = long(last_used_str)
            except NameError:
                last_used = int(last_used_str)

    except Exception as e:
        log.debug('Error reading from %s: %s', used_mem_file, e)
        last_used = None

    with open(used_mem_file, 'w') as fp:
        fp.write(str(current_used))

    return last_used


def _get_meminfo():
    try:
        with open('/proc/meminfo') as fp:
            return fp.read()
    except IOError as e:
        log.debug('Skipping commit memory:%s', e)
