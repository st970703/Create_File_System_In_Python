
#!/usr/bin/env python

from __future__ import print_function, absolute_import, division

import logging
import sys

from fuse import FUSE
from passthrough import Passthrough


class LoggingMixIn:
    log = logging.getLogger('A2')

    def __call__(self, op, path, *args):
        self.log.debug('-> path:%s %s%s', path, op, repr(args))
        ret = '[Unhandled Exception]'
        try:
            ret = getattr(self, op)(path, *args)
            return ret
        except OSError as e:
            ret = str(e)
            raise

class A2Fuse1(LoggingMixIn, Passthrough):

	pass

def main(mountpoint, root):
    FUSE(A2Fuse1(root), mountpoint, nothreads=True, foreground=True)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main(sys.argv[2], sys.argv[1])
