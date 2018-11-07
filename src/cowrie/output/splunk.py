# Copyright (c) 2015 Michel Oosterhof <michel@oosterhof.net>

"""
Splunk HTTP Event Collector (HEC) Connector.
Not ready for production use.
JSON log file is still recommended way to go
"""

from __future__ import absolute_import, division

import json

try:
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO

from twisted.internet import reactor
from twisted.internet.ssl import ClientContextFactory
from twisted.python import log
from twisted.web import client, http_headers
from twisted.web.client import FileBodyProducer

import cowrie.core.output
from cowrie.core.config import CONFIG


class Output(cowrie.core.output.Output):

    def __init__(self):
        """
        Required: token, url
        Optional: index, sourcetype, source, host
        """
        self.token = CONFIG.get('output_splunk', 'token')
        self.url = CONFIG.get('output_splunk', 'url').encode('utf8')
        try:
            self.index = CONFIG.get('output_splunk', 'index')
        except Exception:
            self.index = None
        try:
            self.source = CONFIG.get('output_splunk', 'source')
        except Exception:
            self.source = None
        try:
            self.sourcetype = CONFIG.get('output_splunk', 'sourcetype')
        except Exception:
            self.sourcetype = None
        try:
            self.host = CONFIG.get('output_splunk', 'host')
        except Exception:
            self.host = None

        cowrie.core.output.Output.__init__(self)

    def start(self):
        contextFactory = WebClientContextFactory()
        # contextFactory.method = TLSv1_METHOD
        self.agent = client.Agent(reactor, contextFactory)

    def stop(self):
        pass

    def write(self, logentry):
        for i in list(logentry.keys()):
            # Remove twisted 15 legacy keys
            if i.startswith('log_'):
                del logentry[i]

        splunkentry = {}
        if self.index:
            splunkentry["index"] = self.index
        if self.source:
            splunkentry["source"] = self.source
        if self.sourcetype:
            splunkentry["sourcetype"] = self.sourcetype
        if self.host:
            splunkentry["host"] = self.host
        else:
            splunkentry["host"] = logentry["sensor"]
        splunkentry["event"] = logentry
        self.postentry(splunkentry)

    def postentry(self, entry):
        """
        Send a JSON log entry to Splunk with Twisted
        """
        headers = http_headers.Headers({
            b'User-Agent': [b'Cowrie SSH Honeypot'],
            b'Authorization': [b"Splunk " + self.token.encode('utf8')],
            b'Content-Type': [b'application/json']
        })
        body = FileBodyProducer(BytesIO(json.dumps(entry).encode('utf8')))
        d = self.agent.request(b'POST', self.url, headers, body)

        def cbBody(body):
            return processResult(body)

        def cbPartial(failure):
            """
            Google HTTP Server does not set Content-Length. Twisted marks it as partial
            """
            failure.printTraceback()
            return processResult(failure.value.response)

        def cbResponse(response):
            if response.code == 200:
                return
            else:
                log.msg("SplunkHEC response: {} {}".format(response.code, response.phrase))
                d = client.readBody(response)
                d.addCallback(cbBody)
                d.addErrback(cbPartial)
                return d

        def cbError(failure):
            failure.printTraceback()

        def processResult(result):
            j = json.loads(result)
            log.msg("SplunkHEC response: {}".format(j["text"]))

        d.addCallback(cbResponse)
        d.addErrback(cbError)
        return d


class WebClientContextFactory(ClientContextFactory):

    def getContext(self, hostname, port):
        return ClientContextFactory.getContext(self)
