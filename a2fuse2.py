#!/usr/bin/env python

from __future__ import print_function, absolute_import, division

import logging

import os
import sys
import errno
from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
from time import time

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
        # in user space
        if path not in self.memory.files:
            return super(A2Fuse2, self).open(path, flags)
        # in memory
        else:
            return self.memory.open(path, flags)

    def create(self, path, mode):
        # create in memory
	    UID = os.getuid()
	    GID = os.getgid()
        self.memory.files[path] = dict(st_mode=(S_IFREG | mode), st_nlink=1,
				st_uid=UID, st_gid=GID,
                                st_size=0, st_ctime=time(), st_mtime=time(),
                                st_atime=time())

        self.memory.fd += 1
        return self.memory.fd

    def unlink(self, path):
        # in memory
        if path in self.memory.files:
            return self.memory.unlink(path)
        else:
        # in user space
            return super(A2Fuse2, self).unlink(path)

    def write(self, path, buf, offset, fh):
        # write to memory
        if path in self.memory.files:
            return self.memory.write(path, buf, offset, fh)
        else:
            return super(A2Fuse2, self).write(path, buf, offset, fh)

    def read(self, path, length, offset, fh):
        # memory
        if path in self.memory.files:
            return self.memory.read(path, length, offset, fh)
        # in user space
        else:
            return super(A2Fuse2, self).read(path, length, offset, fh)

    def release(self, path, fh):
        # in memory
        if path in self.memory.files:
	        return self.memory.release(path, fh)
	    # in user space
	    else:
		    return super(A2Fuse2, self).release(path, fh)

    # __init__, getattr, readdir
    # open, create, unlink
    # write, read

    # Filesystem methods
    # ==================
    def access(self, path, mode):
        full_path = super(A2Fuse2, self)._full_path(path)
        logging.debug('access(self, path, mode) '+full_path)
        # if not os.access(full_path, mode):
        #     raise FuseOSError(errno.EACCES)

    def flush(self, path, fh):
        # if file in memory, don't flush
        if path in self.memory.files:
            pass
        else:
            return super(A2Fuse2, self).flush(path, fh)

    # fix touch
    def utimens(self, path, times=None):
        if path in self.memory.files:
            pass
        else:
            return super(A2Fuse2, self).utimens(path)

def main(mountpoint, root):
    FUSE(A2Fuse2(root), mountpoint, nothreads=True, foreground=True)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main(sys.argv[2], sys.argv[1])
