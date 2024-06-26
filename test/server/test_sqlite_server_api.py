#!/usr/bin/env python3

import logging
import sys
import tempfile
import unittest

sys.path.append('.')
from server.sqlite_server_api import SQLiteServerAPI   # noqa: E402

sample_1 = {
    'cruise': {
        'id': 'NBP1406',
        'start': '2019-07-01',
        'end': '2019-12-31'
    },
    'loggers': {
        'knud': {
            'configs': ['knud->off', 'knud->net', 'knud->net/file']
        },
        'gyr1': {
            'configs': ['gyr1->off',  'gyr1->net', 'gyr1->net/file']
        },
        'mwx1': {
            'configs': ['mwx1->off', 'mwx1->net',  'mwx1->net/file']
        },
        's330': {
            'configs': ['s330->off', 's330->net', 's330->net/file']
        }
    },
    'modes': {
        'off': {
            'knud': 'knud->off',
            'gyr1': 'gyr1->off',
            'mwx1': 'mwx1->off',
            's330': 's330->off'
        },
        'port': {
            'knud': 'knud->off',
            'gyr1': 'gyr1->net',
            'mwx1': 'mwx1->net',
            's330': 's330->off'
        },
        'underway': {
            'knud': 'knud->net/file',
            'gyr1': 'gyr1->net/file',
            'mwx1': 'mwx1->net/file',
            's330': 's330->net/file'
        }
    },
    'default_mode': 'off',
    'configs': {
        'knud->off': {},
        'gyr1->off': {},
        'mwx1->off': {},
        's330->off': {},
        'knud->net': {},
        'gyr1->net': {},
        'mwx1->net': {},
        's330->net': {},
        'knud->net/file': {},
        'gyr1->net/file': {},
        'mwx1->net/file': {},
        's330->net/file': {}
    }
}


################################################################################
class TestSQLiteServerAPI(unittest.TestCase):
    ############################
    def test_basic(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            test_database = tmpdirname + '/test_database.sql'

            api = SQLiteServerAPI(database_path=test_database)
            api.load_configuration(sample_1)

            self.assertEqual(api.get_modes(), ['off', 'port', 'underway'])
            self.assertEqual(api.get_active_mode(), 'off')
            self.assertDictEqual(api.get_logger_configs(),
                                 {'gyr1': {'name': 'gyr1->off'},
                                  'knud': {'name': 'knud->off'},
                                  'mwx1': {'name': 'mwx1->off'},
                                  's330': {'name': 's330->off'}})
            self.assertDictEqual(api.get_logger_configs('underway'),
                                 {'gyr1': {'name': 'gyr1->net/file'},
                                  'knud': {'name': 'knud->net/file'},
                                  'mwx1': {'name': 'mwx1->net/file'},
                                  's330': {'name': 's330->net/file'}})

            with self.assertRaises(ValueError):
                api.set_active_mode('invalid mode')

            logging.debug('Setting active mode to "underway"')
            api.set_active_mode('underway')
            self.assertEqual(api.get_active_mode(), 'underway')
            self.assertDictEqual(api.get_logger_configs(),
                                 {'gyr1': {'name': 'gyr1->net/file'},
                                  'knud': {'name': 'knud->net/file'},
                                  'mwx1': {'name': 'mwx1->net/file'},
                                  's330': {'name': 's330->net/file'}})
            logging.debug(f'Logger configs: {api.get_logger_configs()}')

            with self.assertRaises(ValueError):
                api.get_logger_configs('invalid_mode')
            self.assertEqual(api.get_logger_configs('port'),
                             {'gyr1': {'name': 'gyr1->net'},
                              'knud': {'name': 'knud->off'},
                              'mwx1': {'name': 'mwx1->net'},
                              's330': {'name': 's330->off'}})
            self.assertDictEqual(api.get_loggers(),
                                 {'knud': {
                                     'configs': [
                                         'knud->off', 'knud->net', 'knud->net/file'],
                                     'active': 'knud->net/file'
                                 },
                'gyr1': {
                                     'configs': [
                                         'gyr1->off', 'gyr1->net', 'gyr1->net/file'],
                                     'active': 'gyr1->net/file'
                                 },
                'mwx1': {
                                     'configs': [
                                         'mwx1->off', 'mwx1->net', 'mwx1->net/file'],
                                     'active': 'mwx1->net/file'
                                 },
                's330': {
                                     'configs': [
                                         's330->off', 's330->net', 's330->net/file'],
                                     'active': 's330->net/file'}
            })
            api.delete_configuration()
            self.assertEqual(None, api.get_logger_configs())


################################################################################
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbosity', dest='verbosity',
                        default=0, action='count',
                        help='Increase output verbosity')
    args = parser.parse_args()

    LOGGING_FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(format=LOGGING_FORMAT)

    LOG_LEVELS = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}
    args.verbosity = min(args.verbosity, max(LOG_LEVELS))
    logging.getLogger().setLevel(LOG_LEVELS[args.verbosity])

    # logging.getLogger().setLevel(logging.DEBUG)
    unittest.main(warnings='ignore')
