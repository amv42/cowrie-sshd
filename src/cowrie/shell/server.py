# Copyright (c) 2015 Michel Oosterhof <michel@oosterhof.net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. The names of the author(s) may not be used to endorse or promote
#    products derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHORS ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

from __future__ import absolute_import, division

import copy
import json
import random
from configparser import NoOptionError

import twisted.python.log as log

from cowrie.core.config import CONFIG
from cowrie.shell import fs


class CowrieServer(object):
    """
    In traditional Kippo each connection gets its own simulated machine.
    This is not always ideal, sometimes two connections come from the same
    source IP address. we want to give them the same environment as well.
    So files uploaded through SFTP are visible in the SSH session.
    This class represents a 'virtual server' that can be shared between
    multiple Cowrie connections
    """
    fs = None
    process = None
    avatars = []

    def __init__(self, realm):
        self.hostname = CONFIG.get('honeypot', 'hostname')

        try:
            arches = [arch.strip() for arch in CONFIG.get('shell', 'arch').split(',')]
            self.arch = random.choice(arches)
        except NoOptionError:
            self.arch = 'linux-x64-lsb'

        log.msg("Initialized emulated server as architecture: {}".format(self.arch))

    def getCommandOutput(self, file):
        """
        Reads process output from JSON file.
        """
        with open(file) as f:
            cmdoutput = json.load(f)
        return cmdoutput

    def initFileSystem(self):
        """
        Do this so we can trigger it later. Not all sessions need file system
        """
        self.fs = fs.HoneyPotFilesystem(copy.deepcopy(fs.PICKLE), self.arch)

        try:
            self.process = self.getCommandOutput(CONFIG.get('shell', 'processes'))['command']['ps']
        except NoOptionError:
            self.process = None
