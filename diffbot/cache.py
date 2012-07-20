#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:expandtab
"""
    py-diffbot - cache.py

    Caching handlers with support for file, GAE memcache and python memcache

    This source file is subject to the new BSD license that is bundled with this
    package in the file LICENSE.txt. The license is also available online at the
    URL: <http://nikcub.appspot.com/bsd-license.txt>

    :copyright: Copyright (C) 2011 Nik Cubrilovic and others, see AUTHORS
    :license: new BSD, see LICENSE for more details.
"""

__version__ = '0.0.2'
__author__ = 'Nik Cubrilovic <nikcub@gmail.com>'


import os, logging, hashlib, urllib

try:
    from google.appengine.api import memcache
    GAE = True
except ImportError:
    GAE = False
    try:
        import memcache
        LOCAL_MEMCACHE = True
    except ImportError:
        LOCAL_MEMCACHE = False

#---------------------------------------------------------------------------
#     Handler Classes
#---------------------------------------------------------------------------

class CacheHandler(object):

    options = None

    def __init__(self, options):
        self.options = options

    def wrap(self, func):
        def cache(url, data):
            logging.info("Called fetch function with")
            key = self.hash(url + '?' + urllib.urlencode(data))
            cache_store = self.get(key)
            if cache_store:
                return cache_store
            val = func(url, data)
            if val:
                self.set(key, val)
            return val
        return cache

    def hash(self, key):
        return hashlib.sha1(key).hexdigest()

class NullHandler(CacheHandler):
    def __init__(self, options):
        pass

    def wrap(self, func):
        return func

class MemcacheHandler(CacheHandler):

    def fname(self):
        pass

    def fname(self):
        pass


class GAEMemcacheHandler(CacheHandler):
    ttl = 60 * 60 * 24 * 4

    def get(self, key):
        return memcache.get(key)

    def set(self, key, value):
        return memcache.set(key, value, self.ttl)


class FileCacheHandler(CacheHandler):

    cache_folder = None

    def __init__(self, options):
        if options is not None and options.has_key('cache_folder'):
            cf = options['cache_folder']
            if not cf.startswith('/'):
                cf = os.path.join(os.path.dirname(__file__), cf)
            if os.path.isdir(cf):
                self.cache_folder = options['cache_folder']
            else:
                raise Exception("Not a valid cache folder: %s (got: %s)" % (cf, os.path.isdir(cf)))
        else:
            import tempfile
            self.cache_folder = tempfile.gettempdir()

    def get_filepath(self, key):
        return os.path.join(self.cache_folder, "%s.txt" % key)

    def get(self, key):
        file_path = self.get_filepath(key)
        if os.path.isfile(file_path):
            logging.info("CACHE HIT")
            return open(file_path).read()
        return False

    def set(self, key, value):
        file_path = self.get_filepath(key)
        try:
            f = open(file_path, 'w')
            f.write(value)
        except Exception, e:
            logging.error("Exception: could not write file %s" % (file_path))
            logging.exception(e)
            return False
        return True


#---------------------------------------------------------------------------
#     Handler Class
#---------------------------------------------------------------------------


def handler(cache_options = None):
    if cache_options:
        if cache_options.has_key('handler'):
            if cache_options['handler'] == 'memcache' and GAE:
                return GAEMemcacheHandler(cache_options)
            elif cache_options['handler'] == 'memcache' and LOCAL_MEMCACHE:
                return MemcacheHandler(cache_options)
            elif cache_options['handler'] == 'file':
                return FileCacheHandler(cache_options)
    if GAE:
        return GAEMemcacheHandler(cache_options)
    if LOCAL_MEMCACHE and cache_options.has_key('memcache_server'):
        return MemcacheHandler(cache_options)
    return NullHandler(cache_options)
