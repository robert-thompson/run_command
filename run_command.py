#!/usr/bin/env python
'''
Run Linux commands in a Python 2.4 compatible way.

GNU GPL version 3
Copyright 2016 Robert Thompson

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

__version__ = '0.0.1'

import sys
import optparse
import logging
import re
import os
# import os.path
# import time

from subprocess import Popen, PIPE
import shlex
from pipes import quote
import platform


def test(options):
    server = Server()
    print server.distro, server.version

    # Complex strings in command
    cmd = (
        "rpm -q",
        r"--queryformat='%{VERSION}-%{RELEASE}\n'",
        "kernel",
    )
    cmd = " ".join(cmd)
    print server.run_command(cmd)

    # Test shell escapes
    print server.run_command("touch /tmp/test")
    try:
        print server.run_command("ls -l /home; rm /tmp/test")
        print server.run_command("ls -l /home; rm /tmp/test", shell=True)
    except RuntimeError, e:
        if re.search("ls: cannot access rm", str(e)):
            pass
    # Clean up
    print server.run_command("rm /tmp/test")

    fh = open("echo.sh", "w")
    fh.write('''#!/bin/bash
    echo "Running $0"
    for w in $*;
    do
        echo $w
    done
    ''')
    fh.close()
    os.chmod("echo.sh", 0700)
    print server.run_command("./echo.sh 1 2 3", shell=True)
    os.remove("echo.sh")

    # Unsanitize to use shell functions (like expansion).
    print server.run_command("ls -d ~/", shell=True, sanitize=False)

    # Unsanitized and shell must be a string.
    print server.run_command("echo 1 2 3", shell=True, sanitize=False)

    # Unsanitized and no shell must be a list.
    print server.run_command("echo 1 2 3".split(), shell=False, sanitize=False)



class Server(object):
    def __init__(self):
        (distro, version) = platform.dist()[0:2]
        self.distro = distro
        self.version = version

    def run_command(self, command, sanitize=True, shell=False):
        '''Run command and capture the output.'''
        if sanitize:
            command = shlex.split(command)
            if shell:
                if sanitize:
                    command = " ".join([ quote(w) for w in command ])
                else:
                    command = " ".join(command)
        logging.debug("Running command: %s" % repr(command))
        p = Popen(command, stdout=PIPE, stderr=PIPE, shell=shell)
        (stdout, stderr) = p.communicate()
        if p.returncode > 0:
            raise RuntimeError(stderr)
        logging.debug("Output:\n%s" % stdout)
        return stdout.strip()


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-d", "--debug",
                      help="Run in debug mode.",
                      action="store_true", dest="debug", default=False,)
    (options, args) = parser.parse_args()
    if options.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARN
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    test(options)
