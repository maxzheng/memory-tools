from memorytools.loop import main


def test_loop_command(runner):
  result = runner.invoke(main, ['show-mem', '0.01', '-c', 2, '--concurrency', '3'])

  assert result.exit_code == 0
  assert 'Looped 2 times' in result.output
  assert 'with concurrency of 3 (6 runs' in result.output


def test_loop_module(runner):
  result = runner.invoke(main, ['memorytools:summarize_objects', '0.01', '-c', 1])

  assert result.exit_code == 0
  assert 'Looped 1 time' in result.output


def test_loop_code(runner):
  result = runner.invoke(main, ['print("Hello World!")', '0.01', '-c', 10, '-cc', 5])

  assert result.exit_code == 0
  assert 'Looped 10 times' in result.output
  assert 'with concurrency of 5 (50 runs' in result.output
