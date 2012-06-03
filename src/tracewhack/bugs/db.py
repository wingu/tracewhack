"""
Database for bug information.

Talks to remote bug databases and caches information locally.
"""

from collections import defaultdict
from os import path
import shelve

from tracewhack import config, log
from tracewhack.bugs import github

SUPPORTED_DB_TYPES = {'github': github}

VERSION = 1


class BugDb(object):
    """
    Aggregated database for formatted bugs.
    """

    def __init__(self, profile, db_configs, options):
        self.db_configs = db_configs
        self.cache_fname = _cache_fname(profile)
        self.options = options
        self.cache_shelf = None

    def bugs(self):
        """
        Generator to walk all the bugs in the bug db.
        """
        for (key, val) in self.cache_shelf.iteritems():
            if _is_bug_key(key):
                val = val.copy()
                val['global_id'] = key
                yield val

    def open(self):
        """
        Open the bug db, refreshing from remote dbs as specified by
        the refresh option.
        """
        self.cache_shelf = _open_cache_shelf(self.cache_fname)

        if not self.cache_shelf.get('version', None):
            # new shelf
            self.cache_shelf['version'] = VERSION

        if int(self.cache_shelf['version']) != int(VERSION):
            raise RuntimeError("Wrong shelf version %d (code is %d" %
                               (int(self.cache_shelf['version']),
                                int(VERSION)))

        if self.options['refresh'] == 'none':
            log.verbose("Not refreshing any bug dbs due to refresh=none",
                        self.options)
        else:
            self._refresh_from_remotes()

    def close(self):
        """
        Close the bug db.
        """
        if self.cache_shelf:
            self.cache_shelf.close()

    def __enter__(self):
        """
        Open the bug db, refreshing from remote dbs as specified by
        the refresh option.
        """
        self.open()
        return self

    def __exit__(self, extype, value, traceback):
        """
        Close the bug db.
        """
        self.close()

    def _refresh_from_remotes(self):
        """
        Update from remote databases, as specified by the refresh
        behavior.
        """
        grouped_db_configs = defaultdict(lambda: [])

        for db_config in self.db_configs:
            grouped_db_configs[db_config['type'].strip()].append(db_config)

        for (db_type, db_type_configs) in grouped_db_configs.items():
            if db_type not in SUPPORTED_DB_TYPES:
                raise RuntimeError("Unsupported db type: %s" % db_type)
            db_module = SUPPORTED_DB_TYPES[db_type]
            db_module.update(self.cache_shelf,
                             db_type_configs,
                             options=self.options)


def init(profile, db_configs, options):
    """
    Initialize a bug database for the specified profile and return it.
    """
    return BugDb(profile, db_configs, options)


def _cache_fname(profile):
    """
    For a given profile, what's the name of the cache file?
    """
    return path.join(config.TRACEWHACK_DATA_DIR, '%s.shelf' % profile)


def _open_cache_shelf(cache_fname):
    """
    Open the specified cache file, creating it if needed.
    """
    return shelve.open(cache_fname, protocol=2, writeback=False)


def _is_bug_key(key):
    """
    Is this a key for a bug?
    """
    return key and key.startswith('bug:')
