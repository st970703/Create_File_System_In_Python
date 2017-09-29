#!/usr/bin/env python

from __future__ import print_function, absolute_import, division

import logging

import os
import sys
import errno

import memory

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
from passthrough import Passthrough

# elee353, 840454023
class A2Fuse2(LoggingMixIn, Passthrough):

    def __init__(self, root):
        super(self, root)
        self.memory = memory()

    def getattr(self, path, fh=None):
        # in memory
        if path not in self.files:
            full_path = self._full_path(path)
            st = os.lstat(full_path)
            return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                                                            'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size',
                                                            'st_uid'))
        # in user space
        else:
            return self.files[path]

    def readdir(self, path, fh):
        pass

    def open(self, path, flags):
        pass

    def create(self, path, mode, fi=None):
        pass

    def unlink(self, path):
        pass

    def write(self, path, buf, offset, fh):
        pass

    def read(self, path, length, offset, fh):
        pass

        # __init__, getattr, readdir
        # open, create, unlink
        # write, read

def main(mountpoint, root):
    FUSE(A2Fuse2(root), mountpoint, nothreads=True, foreground=True)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main(sys.argv[2], sys.argv[1])
