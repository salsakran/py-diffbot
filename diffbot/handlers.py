#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:expandtab
"""
    py-diffbot - http_client.py

    Python http client library to support Google App Engine urlfetch, urllib
    and urllib2

    This source file is subject to the new BSD license that is bundled with this
    package in the file LICENSE.txt. The license is also available online at the
    URL: <http://nikcub.appspot.com/bsd-license.txt>

    :copyright: Copyright (C) 2011 Nik Cubrilovic and others, see AUTHORS
    :license: new BSD, see LICENSE for more details.
"""

__version__ = '0.0.2'
__author__ = 'Nik Cubrilovic <nikcub@gmail.com>'

GAE = True

import logging

try:
    from google.appengine.api import urlfetch
except ImportError:
    GAE = False
import urllib

from cache import handler as cache_handler

class HttpHandler(object):

    _req_headers = {
        "User-Agent": "py-diffbot v0.0.2 <+http://bitbucket.org/nik/py-diffbot>"
    }
    _req_attempts = 3

    def __init__(self, cache_options = None):
        """docstring for __init__"""
        self._cache_handle = cache_handler(cache_options)
        if self._cache_handle:
            self.get = self._cache_handle.wrap(self.get)
            self.post = self._cache_handle.wrap(self.post)

    def cache_handler(self):
        return self._cache_handle

    def __get__(self, **kwargs):
        logging.debug("Called __call__ with:")
        logging.debug(**kwargs)

    def get(self, url, data):
            return self.fetch(url, data, 'GET')

    def post(self, url, data):
            return self.fetch(url, data, 'POST')

# TODO Somebody who knows the Appengine API should fix this to function the same way as the urllib version
class UrlfetchHandler(HttpHandler):

    def fetch(self, url, data, method):
        attempt = 1
        result = None
        self._req_headers['Connection'] = 'Close'

        while attempt <= self._req_attempts:
            try:
                result = urlfetch.fetch(
                    url,
                    method = urlfetch.GET,
                    headers = self._req_headers,
                    deadline = 20
                )
            except urlfetch.DownloadError, e:
                logging.info("DiffBot: (Download Attempt [%d/%d]) DownloadError: Download timed out"
                    % (attempt, self._req_attempts))
                attempt += 1
            except Exception, e:
                logging.exception("Diffbot: Exception: %s" % e.message)
                logging.exception("Diffbot: Exceeded number of attempts allowed")
                return False

            if result:
                if result.status_code == 200:
                    return result.content

        return False


class UrllibHandler(HttpHandler):

    def fetch(self, url, data, method):
        assert method in ['GET', 'POST']

        result = None

        try:
            if method == 'GET':
                fh = urllib.urlopen(url + '?' + urllib.urlencode(data))
            elif method == 'POST':
                fh = urllib.urlopen(url, urllib.urlencode(data))
            if fh.getcode() != 200:
                logging.error("urllib http request returned status code: %s" % fh.getcode())
                return False
            result = fh.read()
        except Exception, e:
            logging.exception("urllib error: %s", str(e))
            return False

        return result

# TODO implement this?
class Urllib2Handler(HttpHandler):
    def fetch(self, url, data, method):
        import urllib2

        try:
            request = urllib2.Request(
                url,
                # api_args,
                # headers
                )
            handle = urllib2.urlopen(request)
            response = handle.read()
            return response

        except urllib2.URLError, e:
            logging.exception(e)
            return False

# TODO implement options
# TODO return an instance rather than the class (ie. pass and wrap options) and
# TODO select the class to use based on the options (same as cache.py)
def handler(options = None):
    """return a valid HTTP handler for the request"""
    if GAE:
        return    UrlfetchHandler
    return UrllibHandler

