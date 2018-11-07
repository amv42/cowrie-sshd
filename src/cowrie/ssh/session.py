# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
This module contains ...
"""

from __future__ import absolute_import, division

from twisted.conch.ssh import session
from twisted.conch.ssh.common import getNS
from twisted.python import log


class HoneyPotSSHSession(session.SSHSession):
    """
    This is an SSH channel that's used for SSH sessions
    """

    def __init__(self, *args, **kw):
        session.SSHSession.__init__(self, *args, **kw)

    def request_env(self, data):
        name, rest = getNS(data)
        value, rest = getNS(rest)
        if rest:
            raise ValueError("Bad data given in env request")
        log.msg(eventid='cowrie.client.var', format="request_env: %(name)s=%(value)s",
                name=name, value=value)
        # FIXME: This only works for shell, not for exec command
        if self.session:
            self.session.environ[name] = value
        return 0

    def request_agent(self, data):
        log.msg("request_agent: {}".format(repr(data)))
        return 0

    def request_x11_req(self, data):
        log.msg("request_x11: {}".format(repr(data)))
        return 0

    def closed(self):
        """
        This is reliably called on session close/disconnect and calls the avatar
        """
        session.SSHSession.closed(self)
        self.client = None

    def eofReceived(self):
        """
        Redirect EOF to emulated shell. If shell is gone, then disconnect
        """
        if self.session:
            self.session.eofReceived()
        else:
            self.loseConnection()

    def sendEOF(self):
        """
        Utility function to request to send EOF for this session
        """
        self.conn.sendEOF(self)

    def sendClose(self):
        """
        Utility function to request to send close for this session
        """
        self.conn.sendClose(self)

    def channelClosed(self):
        log.msg("Called channelClosed in SSHSession")
