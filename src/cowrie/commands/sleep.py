# Copyright (c) 2015 Michel Oosterhof <michel@oosterhof.net>
# All rights reserved.

"""
This module contains the sleep command
"""

from __future__ import absolute_import, division

from twisted.internet import reactor

from cowrie.shell.command import HoneyPotCommand

commands = {}


class command_sleep(HoneyPotCommand):
    """
    Sleep
    """

    def done(self):
        self.exit()

    def start(self):
        if len(self.args) == 1:
            _time = int(self.args[0])
            self.scheduled = reactor.callLater(_time, self.done)
        else:
            self.write('usage: sleep seconds\n')
            self.exit()


commands['/bin/sleep'] = command_sleep
commands['sleep'] = command_sleep
