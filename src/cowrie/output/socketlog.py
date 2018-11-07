# encoding: utf-8

from __future__ import absolute_import, division

import json
import socket

import cowrie.core.output
from cowrie.core.config import CONFIG


class Output(cowrie.core.output.Output):
    def __init__(self):
        addr = CONFIG.get('output_socketlog', 'address')
        self.host = addr.split(':')[0]
        self.port = int(addr.split(':')[1])

        self.timeout = CONFIG.getint('output_socketlog', 'timeout')
        cowrie.core.output.Output.__init__(self)

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect((self.host, self.port))

    def stop(self):
        self.sock.close()

    def write(self, logentry):
        for i in list(logentry.keys()):
            # Remove twisted 15 legacy keys
            if i.startswith('log_'):
                del logentry[i]

        message = json.dumps(logentry) + '\n'

        try:
            self.sock.sendall(message)
        except socket.error as ex:
            if ex.errno == 32:  # Broken pipe
                self.start()
                self.sock.sendall(message)
            else:
                raise
