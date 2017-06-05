#!/usr/bin/env python

from multiprocessing import Pool
import signal
import time

try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess

import click


@click.command()
@click.argument('command_or_code')
@click.argument('delay', type=float)
@click.option('-c', '--count', 'max_count', type=int, help='Number of times to loop. [default: forever]')
@click.option('-cc', '--concurrency', type=int, default=1, show_default=True, help='Number of concurrent runs per loop.')
@click.help_option('-h')
def main(command_or_code, delay, max_count, concurrency):

    if concurrency < 1:
        raise click.BadParameter('Concurrency must be greater than 1')

    if max_count and max_count < 1:
        raise click.BadParameter('Count must be greater than 1')

    if delay <= 0:
        raise click.BadParameter('Delay must be greater than 0')

    pool = Pool(concurrency, lambda: signal.signal(signal.SIGINT, signal.SIG_IGN))
    count = 0
    start_time = time.time()

    try:
        while True:
            results = pool.map_async(run_command_or_code, [command_or_code] * concurrency)
            results.wait()

            count += 1
            if max_count and count >= max_count:
                break

            time.sleep(delay)

    except KeyboardInterrupt:
        pass

    finally:
        pool.terminate()
        pool.join()

        total_time = time.time() - start_time
        click.echo(('\nLooped %d time%s' % (count, 's' if count > 1 else ''))
                   + (' in %.2f secs' % total_time)
                   + (' with concurrency of %d (%d runs, %.2f secs per loop, %.2f secs per run)' %
                      (concurrency, count * concurrency, total_time / count, total_time / count / concurrency) if concurrency > 1 else ''))


def run_command_or_code(command_or_code):
    try:
        # module:method
        if ':' in command_or_code:
            module_name, method_name = command_or_code.split(':', 1)

            module = __import__(module_name)
            method = getattr(module, method_name)

            return method()

        # code
        elif ' ' in command_or_code:

            exec(command_or_code)

        # command
        else:
            subprocess.call(command_or_code, shell=True)

    except Exception as e:
        click.echo(str(e))
