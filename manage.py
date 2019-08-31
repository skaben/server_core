#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skaben.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    if 'test' in sys.argv and 'keepdb' in sys.argv:
        # and this allows you to use --keepdb to skip re-creating the db,
        # even faster!
        DATABASES['default']['TEST']['NAME'] = \
            '/dev/shm/myproject.test.db.sqlite3'

    execute_from_command_line(sys.argv)
