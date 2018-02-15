"""
This module provides communication capabilities with external program using subprocess.
"""

import subprocess as sp
import os
import sys
import six
import re

class Subprocess(object):
    """Class for interfacing with external programs using subprocess module."""
    def __init__(self, cmd):
        """Opens up an interactive session with cmd."""
        subproc_args = {
            'stdin': sp.PIPE, 
            'stdout': sp.PIPE,
            'stderr': sp.STDOUT, 
            'cwd': '.', 
            #'universal_newlines': True,
            'close_fds': sys.platform != "win32"
        }
        try:
            env = os.environ.copy()
            self.proc = sp.Popen('bash -c "{0}"'.format(cmd), env=env,
                                shell=True, **subproc_args)
        except OSError:
            raise
        self.stdout = self.proc.stdout
        self.stdin = self.proc.stdin

    def __del__(self):
        """clean up process."""
        self.proc.stdin.close()
        try:
            self.proc.kill()
            self.proc.wait()
        except:
            pass

    def query(self, inp):
        """Query an input through stdin and get a response from stdout."""
        pattern = r'EOS'
        self.proc.stdin.write(inp.encode('utf-8') + six.b('\n'))
        self.proc.stdin.flush()
        result = ""
        while True:
            line = self.stdout.readline()[:-1].decode('utf-8')
            if re.search(pattern, line):
                break
            result = "{0}{1}\n".format(result, line)
        return result
