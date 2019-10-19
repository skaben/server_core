from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError


class TestCommands:

    def test_wait_for_db_ready(self):
        """Test connection to db when db is available """
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True
            call_command('wait_for_db')
            assert gi.call_count == 1, 'wrong number of command calls'

    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):
        """ Test waiting for DB """
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')
            assert gi.call_count == 6, 'wrong number of command calls'
