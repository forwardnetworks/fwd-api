import argparse
import os
import sys

try:
    from fwd_api import fwd, properties
except:
    print('Error importing from fwd_api. Check that you ran ' +
          'setup (see README).')
    sys.exit(-1)


class TestParams(object):
    """Utility class to parse and wrap arguments used for tests
    """

    def __init__(self, fwd, snapshot_id):
        """
        @param {fwd} fwd
        @param {int} snapshot_id
        """
        self._fwd = fwd
        self._snapshot_id = snapshot_id

    def get_fwd(self):
        return self._fwd

    def get_snapshot_id(self):
        return self._snapshot_id

    @classmethod
    def load_from_args(cls):
        """Generate a TestParams object by parsing CLI arguments
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('--snapshot-id',
                            help='The id of the snapshot to test',
                            required=True, type=int)
        parser.add_argument('--properties-file',
                            help=('Properties file containing server url, ' +
                                  'username, and password (See ' +
                                  'fwd.properties.example). If this option ' +
                                  'is not set, then the script looks in ' +
                                  '~/.fwd/fwd.properties.'),
                            required=False, type=str)
        parser.add_argument('--verbose', action='store_true',
                            help='Whether to print commands to stdout as run')

        parsed = parser.parse_args()
        prop_file = None
        if parsed.properties_file is not None:
            prop_file = os.path.abspath(parsed.properties_file)
        props = properties.get_properties(prop_file)

        f = fwd.Fwd(props.url, props.username, props.password, parsed.verbose,
                    verify_ssl_cert=False)
        return TestParams(f, parsed.snapshot_id)
