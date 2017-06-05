import sys

from mock import patch, call

from memorytools import save_objects


@patch('os.getpid', return_value=12345)
@patch('memorytools.open')
def test_save_objects(mocked_open, mocked_getpid):
    obj = object()
    objects = [1, 2, {'hello': 'world'}, ['goodbye', 'world'], 'string', True, 1.0, 987984759274549875345987, set([1, 2]), save_objects, obj]

    summary = save_objects(objects)

    if sys.version_info >= (3, 0):
        assert summary == 'Wrote 11 objects to /var/tmp/objects-12345 (943 bytes)'
        assert mocked_open().__enter__().write.call_count == 14

    else:
        assert summary == 'Wrote 11 objects to /var/tmp/objects-12345 (911 bytes)'
        assert mocked_open().__enter__().write.call_args_list == [
            call('Objects count: %d\n' % len(objects)),
            call('Objects size: 911\n\n'),
            call("Objects summary:\n"
                 "      Size Count Type\n"
                 "       280     1 <type 'dict'>\n"
                 "       232     1 <type 'set'>\n"
                 "       120     1 <type 'function'>\n"
                 "        88     1 <type 'list'>\n"
                 "        48     2 <type 'int'>\n"
                 "        43     1 <type 'str'>\n"
                 "        36     1 <type 'long'>\n"
                 "        24     1 <type 'float'>\n"
                 "        24     1 <type 'bool'>\n"
                 "        16     1 <type 'object'>\n\n"
                 "Count       Size Type\n"
                 "    2         48 <type 'int'>\n"
                 "    1        280 <type 'dict'>\n"
                 "    1        232 <type 'set'>\n"
                 "    1        120 <type 'function'>\n"
                 "    1         88 <type 'list'>\n"
                 "    1         43 <type 'str'>\n"
                 "    1         36 <type 'long'>\n"
                 "    1         24 <type 'float'>\n"
                 "    1         24 <type 'bool'>\n"
                 "    1         16 <type 'object'>\n\n"),
            call("IDX 2: 280 <type 'dict'> {'hello': 'world'}\n"),
            call("IDX 8: 232 <type 'set'> set([1, 2])\n"),
            call("IDX 9: 120 <type 'function'> %s\n" % str(save_objects)),
            call("IDX 3: 88 <type 'list'> ['goodbye', 'world']\n"),
            call("IDX 4: 43 <type 'str'> string\n"),
            call("IDX 7: 36 <type 'long'> 987984759274549875345987\n"),
            call("IDX 6: 24 <type 'float'> 1.0\n"),
            call("IDX 5: 24 <type 'bool'> True\n"),
            call("IDX 1: 24 <type 'int'> 2\n"),
            call("IDX 0: 24 <type 'int'> 1\n"),
            call("IDX 10: 16 <type 'object'> %s\n" % str(obj))
        ]
