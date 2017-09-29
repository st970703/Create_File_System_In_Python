#!/usr/bin/env python

from __future__ import print_function, absolute_import, division

import logging

import os
import sys
import errno

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
from passthrough import Passthrough
from memory import Memory

# elee353, 840454023
class A2Fuse2(LoggingMixIn, Passthrough):

    def __init__(self, root):
        Passthrough.__init__(self, root)
        # add memory field
        self.memory = Memory()

    def getattr(self, path, fh=None):
        # in user space
        if path in self._full_path(path):
            return self.getattr(self, path, fh=None)
        else:
            # in memory
            return self.memory.getattr(self, path, fh=None)

    def readdir(self, path, fh):
        if path in self:
            return self.readdir(self, path, fh)
        else:
            return self.memory.readdir(self, path, fh)

    def open(self, path, flags):
        if path in self:
            return self.open(self, path, flags)
        else:
            return self.memory.open(self, path, flags)

    def create(self, path, mode, fi=None):
        if path in self:
            return self.create(self, path, mode)
        else:
            return self.memory.create(self, path, mode)

    def unlink(self, path):
        if path in self:
            return self.unlink(self, path)
        else:
            return self.memory.unlink(self, path)

    def write(self, path, buf, offset, fh):
        if path in self:
            return self.write(self, path, buf, offset, fh)
        else:
            return self.memory.write(self, path, buf, offset, fh)

    def read(self, path, length, offset, fh):
        if path in self:
            return self.read(self, path, buf, offset, fh)
        else:
            return self.memory.read(self, path, buf, offset, fh)
            # __init__, getattr, readdir
            # open, create, unlink
            # write, read

def main(mountpoint, root):
    FUSE(A2Fuse2(root), mountpoint, nothreads=True, foreground=True)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main(sys.argv[2], sys.argv[1])
