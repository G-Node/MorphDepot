# Base classes for morphfs

from __future__ import division, unicode_literals, print_function

import errno
from log import logged
from defaultfs import DefaultFS
from fshelper import Path
from fsmapping import RootDir


class MorphFS(DefaultFS):
    """
    Main fuse interface of the morphdepot file system.
    """

    @logged
    def __init__(self, *args, **kwargs):
        super(MorphFS, self).__init__(*args, **kwargs)
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


