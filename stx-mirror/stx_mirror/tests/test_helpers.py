from test_common import StxTest
from helpers import Komander


class TestKomander(StxTest):

    def test_successful_command(self):
        test_command = 'uname'
        obj = Komander()
        results = obj.run(test_command)
        self.assertEquals(results.retcode, 0)
        self.assertEquals(results.stdout, 'Linux\n')

    def test_unsuccessful_command(self):
        test_command = 'ls3'
        obj = Komander()
        results = obj.run(test_command)
        self.assertEquals(results.retcode, 127)

    def test_timeout_command(self):
        test_command = 'sleep 5'
        obj = Komander()
        results = obj.run(test_command, timeout=1)
        self.assertEquals(results.retcode, -9)
