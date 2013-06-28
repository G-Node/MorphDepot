#!/usr/bin/env python

from __future__ import division, unicode_literals, print_function

import fuse
from morphdepot.morphfs import MorphFS

fuse.fuse_python_api = (0, 2)

usage = "usage"
server = MorphFS(version="%prog " + fuse.__version__,
                 dash_s_do='setsingle',
                 usage=usage)
server.parse(errex=1)
server.multithreaded = 0
try:
    server.main()
except fuse.FuseError, e:
    print(str(e))
