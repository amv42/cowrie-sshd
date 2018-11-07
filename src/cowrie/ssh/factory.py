# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
This module contains ...
"""

from __future__ import absolute_import, division

import time
from configparser import NoOptionError

from twisted.conch.openssh_compat import primes
from twisted.conch.ssh import factory
from twisted.conch.ssh import keys
from twisted.python import log

from cowrie.core.config import CONFIG
from cowrie.ssh import connection
from cowrie.ssh import keys as cowriekeys
from cowrie.ssh import transport
from cowrie.ssh import userauth


class CowrieSSHFactory(factory.SSHFactory):
    """
    This factory creates HoneyPotSSHTransport instances
    They listen directly to the TCP port
    """

    services = {
        b'ssh-userauth': userauth.HoneyPotSSHUserAuthServer,
        b'ssh-connection': connection.CowrieSSHConnection,
    }
    starttime = None
    privateKeys = None
    publicKeys = None
    primes = None
    tac = None  # gets set later

    def logDispatch(self, *msg, **args):
        """
        Special delivery to the loggers to avoid scope problems
        """
        args['sessionno'] = 'S{0}'.format(args['sessionno'])
        for dblog in self.tac.dbloggers:
            dblog.logDispatch(*msg, **args)
        for output in self.tac.output_plugins:
            output.logDispatch(*msg, **args)

    def startFactory(self):
        # For use by the uptime command
        self.starttime = time.time()

        # Load/create keys
        rsaPubKeyString, rsaPrivKeyString = cowriekeys.getRSAKeys()
        dsaPubKeyString, dsaPrivKeyString = cowriekeys.getDSAKeys()
        self.publicKeys = {
            b'ssh-rsa': keys.Key.fromString(data=rsaPubKeyString),
            b'ssh-dss': keys.Key.fromString(data=dsaPubKeyString)
        }
        self.privateKeys = {
            b'ssh-rsa': keys.Key.fromString(data=rsaPrivKeyString),
            b'ssh-dss': keys.Key.fromString(data=dsaPrivKeyString)
        }

        _modulis = '/etc/ssh/moduli', '/private/etc/moduli'
        for _moduli in _modulis:
            try:
                self.primes = primes.parseModuliFile(_moduli)
                break
            except IOError:
                pass

        try:
            self.ourVersionString = CONFIG.get('ssh', 'version')
        except NoOptionError:
            self.ourVersionString = 'SSH-2.0-OpenSSH_6.0p1 Debian-4+deb7u2'

        factory.SSHFactory.startFactory(self)
        log.msg("Ready to accept SSH connections")

    def stopFactory(self):
        factory.SSHFactory.stopFactory(self)

    def buildProtocol(self, addr):
        """
        Create an instance of the server side of the SSH protocol.

        @type addr: L{twisted.internet.interfaces.IAddress} provider
        @param addr: The address at which the server will listen.

        @rtype: L{cowrie.ssh.transport.HoneyPotSSHTransport}
        @return: The built transport.
        """

        t = transport.HoneyPotSSHTransport()

        t.ourVersionString = self.ourVersionString
        t.supportedPublicKeys = list(self.privateKeys.keys())

        if not self.primes:
            ske = t.supportedKeyExchanges[:]
            if b'diffie-hellman-group-exchange-sha1' in ske:
                ske.remove(b'diffie-hellman-group-exchange-sha1')
                log.msg("No moduli, no diffie-hellman-group-exchange-sha1")
            if b'diffie-hellman-group-exchange-sha256' in ske:
                ske.remove(b'diffie-hellman-group-exchange-sha256')
                log.msg("No moduli, no diffie-hellman-group-exchange-sha256")
            t.supportedKeyExchanges = ske

        # Reorder supported ciphers to resemble current openssh more
        t.supportedCiphers = [
            b'aes128-ctr',
            b'aes192-ctr',
            b'aes256-ctr',
            b'aes128-cbc',
            b'3des-cbc',
            b'blowfish-cbc',
            b'cast128-cbc',
            b'aes192-cbc',
            b'aes256-cbc'
        ]
        t.supportedPublicKeys = [b'ssh-rsa', b'ssh-dss']
        t.supportedMACs = [b'hmac-md5', b'hmac-sha1']
        t.supportedCompressions = [b'zlib@openssh.com', b'zlib', b'none']

        t.factory = self
        return t
