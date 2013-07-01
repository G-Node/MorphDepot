# Base classes for morphfs

from __future__ import division, unicode_literals, print_function

import errno
import fuse
import stat
import time
from log import logged
from defaultfs import DefaultFS
from fsmapping import RootDir


class MorphFS(DefaultFS):
    """
    Main fuse interface of the morphdepot file system.
    """

    @logged
    def __init__(self, *args, **kwargs):
        DefaultFS.__init__(self, *args, **kwargs)
        self.__root = RootDir()

    @property
    def root(self):
        return self.__root

    @logged
    def getattr(self, path):
        f = self.root.resolve(path)
        if f is not None:
            return f.getattr()
        else:
            return -errno.ENOENT

