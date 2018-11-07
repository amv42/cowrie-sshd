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

import twisted
from twisted.conch import interfaces as conchinterfaces
from twisted.conch.telnet import ITelnetProtocol
from twisted.python import log

from zope.interface import implementer

from cowrie.core.config import CONFIG
from cowrie.proxy import avatar as proxyavatar
from cowrie.proxy import server as proxyserver
from cowrie.shell import avatar as shellavatar
from cowrie.shell import server as shellserver
from cowrie.telnet import session


@implementer(twisted.cred.portal.IRealm)
class HoneyPotRealm(object):

    def __init__(self):
        pass

    def requestAvatar(self, avatarId, mind, *interfaces):
        try:
            backend = CONFIG.get('honeypot', 'backend')
        except Exception:
            backend = 'shell'

        if backend == 'shell':
            if conchinterfaces.IConchUser in interfaces:
                serv = shellserver.CowrieServer(self)
                user = shellavatar.CowrieUser(avatarId, serv)
                return interfaces[0], user, user.logout
            elif ITelnetProtocol in interfaces:
                serv = shellserver.CowrieServer(self)
                user = session.HoneyPotTelnetSession(avatarId, serv)
                return interfaces[0], user, user.logout
            raise NotImplementedError("No supported interfaces found.")
        elif backend == 'proxy':
            if conchinterfaces.IConchUser in interfaces:
                serv = proxyserver.CowrieServer(self)
                user = proxyavatar.CowrieUser(avatarId, serv)
                return interfaces[0], user, user.logout
            elif ITelnetProtocol in interfaces:
                raise NotImplementedError("Telnet not yet supported for proxy mode.")
            log.msg('No supported interfaces found.')
            raise NotImplementedError("No supported interfaces found.")
        else:
            raise NotImplementedError("No supported backend found.")
