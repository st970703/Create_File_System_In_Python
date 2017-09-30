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
        logging.debug('__init__(self, root) '+root)

        Passthrough.__init__(self, root)
        # add memory field
        self.memory = Memory()

    def getattr(self, path, fh=None):
        # in memory
        if path in self.memory.files:
            # error check
            if path not in self.memory.files:
                raise FuseOSError(ENOENT)
            return self.memory.files[path]
        else:
            # in user space
            full_path = super(A2Fuse2, self)._full_path(path)
            logging.debug("Path in getattr is: " + full_path)
            st = os.lstat(full_path)
            return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                                        'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size',
                                        'st_uid'))

    def readdir(self, path, fh):
        full_path = super(A2Fuse2, self)._full_path(path)
        logging.debug("READDIR fullpath is=" + full_path)
        dirents = ['.', '..']
        if os.path.isdir(full_path):
            dirents.extend(os.listdir(full_path))
        for r in dirents:
            logging.debug("yield r " + r)
            yield r
        for x in self.memory.files:
            if x != '/':
                logging.debug("yield x " + x)
                yield x[1:]

    def open(self, path, flags):
        if path not in self.memory.files:
            return super(A2Fuse2, self).open(self, path, flags)
        else:
            return self.memory.open(self, path, flags)

    def create(self, path, mode, fi=None):
        if path not in self.memory.files:
            return super(A2Fuse2, self).create(self, path, mode)
        else:
            return self.memory.create(self, path, mode)

    def unlink(self, path):
        if path not in self.memory.files:
            return super(A2Fuse2, self).unlink(self, path)
        else:
            return self.memory.unlink(self, path)

    def write(self, path, buf, offset, fh):
        if path not in self.memory.files:
            return super(A2Fuse2, self).write(self, path, buf, offset, fh)
        else:
            return self.memory.write(self, path, buf, offset, fh)

    def read(self, path, length, offset, fh):
        if path not in self.memory.files:
            return super(A2Fuse2, self).read(self, path, length, offset, fh)
        else:
            return self.memory.read(self, path, length, offset, fh)

    # __init__, getattr, readdir
    # open, create, unlink
    # write, read

    # Filesystem methods
    # ==================
    def access(self, path, mode):
        full_path = super(A2Fuse2, self)._full_path(path)
        logging.debug('access(self, path, mode) '+full_path)
        if not os.access(full_path, mode):
            raise FuseOSError(errno.EACCES)

def main(mountpoint, root):
    FUSE(A2Fuse2(root), mountpoint, nothreads=True, foreground=True)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main(sys.argv[2], sys.argv[1])
