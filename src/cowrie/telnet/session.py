# Copyright (C) 2015, 2016 GoSecure Inc.
"""
Telnet User Session management for the Honeypot

@author: Olivier Bilodeau <obilodeau@gosecure.ca>
"""

from __future__ import absolute_import, division

import traceback

from twisted.conch.ssh import session
from twisted.conch.telnet import ECHO, SGA, TelnetBootstrapProtocol
from twisted.internet import interfaces, protocol
from twisted.python import log

from zope.interface import implementer

from cowrie.insults import insults
from cowrie.shell import protocol as cproto
from cowrie.shell import pwd


class HoneyPotTelnetSession(TelnetBootstrapProtocol):
    id = 0  # telnet can only have 1 simultaneous session, unlike SSH
    windowSize = [40, 80]

    def __init__(self, username, server):
        self.username = username.decode()
        self.server = server

        try:
            pwentry = pwd.Passwd().getpwnam(self.username)
            self.uid = pwentry["pw_uid"]
            self.gid = pwentry["pw_gid"]
            self.home = pwentry["pw_dir"]
        except Exception:
            self.uid = 1001
            self.gid = 1001
            self.home = '/home'

        self.environ = {
            'LOGNAME': self.username,
            'USER': self.username,
            'SHELL': '/bin/bash',
            'HOME': self.home,
            'TMOUT': '1800'}

        if self.uid == 0:
            self.environ['PATH'] = '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
        else:
            self.environ['PATH'] = '/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games'

        # required because HoneyPotBaseProtocol relies on avatar.avatar.home
        self.avatar = self

        # to be populated by HoneyPotTelnetAuthProtocol after auth
        self.transportId = None

        # Do the delayed file system initialization
        self.server.initFileSystem()

    def connectionMade(self):
        processprotocol = TelnetSessionProcessProtocol(self)

        # If we are dealing with a proper Telnet client: enable server echo
        if self.transport.options:
            self.transport.willChain(SGA)
            self.transport.willChain(ECHO)

        self.protocol = insults.LoggingTelnetServerProtocol(
            cproto.HoneyPotInteractiveTelnetProtocol, self)

        # somewhere in Twisted this exception gets lost. Log explicitly here
        try:
            self.protocol.makeConnection(processprotocol)
            processprotocol.makeConnection(session.wrapProtocol(self.protocol))
        except Exception:
            log.msg(traceback.format_exc())

    def connectionLost(self, reason):
        TelnetBootstrapProtocol.connectionLost(self, reason)
        self.server = None
        self.avatar = None
        self.protocol = None

    def logout(self):
        log.msg('avatar {} logging out'.format(self.username))


# Taken and adapted from
# https://github.com/twisted/twisted/blob/26ad16ab41db5f0f6d2526a891e81bbd3e260247/twisted/conch/ssh/session.py#L186
@implementer(interfaces.ITransport)
class TelnetSessionProcessProtocol(protocol.ProcessProtocol):
    """
    I am both an L{IProcessProtocol} and an L{ITransport}.
    I am a transport to the remote endpoint and a process protocol to the
    local subsystem.
    """

    def __init__(self, sess):
        self.session = sess
        self.lostOutOrErrFlag = False

    def outReceived(self, data):
        self.session.write(data)

    def errReceived(self, err):
        log.err("Error received: {}".format(err))
        # EXTENDED_DATA_STDERR is from ssh, no equivalent in telnet?
        # self.session.writeExtended(connection.EXTENDED_DATA_STDERR, err)

    def outConnectionLost(self):
        """
        EOF should only be sent when both STDOUT and STDERR have been closed.
        """
        if self.lostOutOrErrFlag:
            self.session.conn.sendEOF(self.session)
        else:
            self.lostOutOrErrFlag = True

    def errConnectionLost(self):
        """
        See outConnectionLost().
        """
        self.outConnectionLost()

    def connectionLost(self, reason=None):
        self.session.loseConnection()
        self.session = None

    def processEnded(self, reason=None):
        """
        here SSH is doing signal handling, I don't think telnet supports that so
        I'm simply going to bail out
        """
        log.msg("Process ended. Telnet Session disconnected: {}".format(reason))
        self.session.loseConnection()

    def getHost(self):
        """
        Return the host from my session's transport.
        """
        return self.session.transport.getHost()

    def getPeer(self):
        """
        Return the peer from my session's transport.
        """
        return self.session.transport.getPeer()

    def write(self, data):
        self.session.write(data)

    def writeSequence(self, seq):
        self.session.write(b''.join(seq))

    def loseConnection(self):
        self.session.loseConnection()
