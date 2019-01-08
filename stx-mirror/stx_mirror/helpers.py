import tempfile
import time
import threading
import subprocess

class Komander(object):
    """ Launch commands and returns the output """

    @staticmethod
    def run(cmd, timeout=0):
        """
        Executes a command in the shell,
        Returns a ShellCommand object with the results
        """
        tmp_stdout = tempfile.SpooledTemporaryFile()
        tmp_stderr = tempfile.SpooledTemporaryFile()

        command = ShellCommand(cmd)
        p = subprocess.Popen(command.cmd, stdout=tmp_stdout,
                             stderr=tmp_stderr, shell=True)

        # Wait for subprocess to complete.

        if timeout > 0:
            while p.poll() is None and timeout > 0:
                time.sleep(0.25)
                timeout -= 0.25
            p.kill()

        p.communicate()
        tmp_stdout.seek(0)
        tmp_stderr.seek(0)

        command.stdout = tmp_stdout.read()
        command.stderr = tmp_stderr.read()
        command.retcode = p.returncode

        tmp_stdout.close()
        tmp_stderr.close()

        return command

class ShellCommand(object):
    """ Represents a shell command """

    def __init__(self, cmd=""):
        self.cmd = cmd
        self.stdout = ""
        self.stderr = ""
        self.retcode = ""

    def __str__(self):
        msg = "Command : {0}\nstdout = {1}\nstderr = {2}\nretcode = {3}"
        return msg.format(self.cmd,
                          self.stdout,
                          self.stderr,
                          self.retcode)
