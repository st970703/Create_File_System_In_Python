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
        # add memory field
        self.memory = memory(self)

    def getattr(self, path, fh=None):
        # in user space
        if (#in user space):
            return self.getattr(self, path, fh=None)
        else:
            # in memory
            return self.memory.getattr(self, path, fh=None)

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
