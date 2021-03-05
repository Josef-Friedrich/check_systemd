import unittest
from helper import execute_main


class TestMock(unittest.TestCase):

    def test_multiple_units(self):
        result = execute_main()
        self.assertEqual(result.exitcode, 0)
        self.assertEqual(
            'SYSTEMD OK - all | count_units=386 startup_time=12.345;60;120 '
            'units_activating=0 units_active=275 units_failed=0 '
            'units_inactive=111',
            result.first_line
        )


if __name__ == '__main__':
    unittest.main()
