# Base classes for morphfs

from __future__ import division, unicode_literals, print_function

import errno
import config
import sqlalchemy
import sqlalchemy.orm as orm
import fuse
from log import logged
import models.morph
from models.morph import Base
from defaultfs import DefaultFS
from fsmapping import RootDir


class MorphFS(DefaultFS):
    """
    Main fuse interface of the morphdepot file system.
    """

    @logged
    def __init__(self, *args, **kwargs):
        super(MorphFS, self).__init__(*args, **kwargs)
        s = self.init_session()
        self.__root = RootDir(s)

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

    @logged
    def open(self, path, flags):
        f = self.root.resolve(path)
        if f is not None:
            if f.is_file():
                # TODO check permissions
                return None
            else:
                return -errno.EOPNOTSUPP
        else:
            return -errno.ENOENT

    @logged
    def read(self, path, size, offset, fh=None):
        f = self.root.resolve(path)
        if f is not None:
            if f.is_file():
                # TODO check permissions
                return f.read(size, offset)
            else:
                return -errno.EOPNOTSUPP
        else:
            return -errno.ENOENT

    @logged
    def write(self, path, buf, offset, fh=None):
        f = self.root.resolve(path)
        if f is not None:
            if f.is_file():
                # TODO check permissions
                return f.write(buf, offset)
            else:
                return -errno.EOPNOTSUPP
        else:
            return -errno.ENOENT

    @logged
    def opendir(self, path):
        """ everything is accessible """
        # TODO get permissions from the resolved object
        return 0

    @logged
    def readdir(self, path, offset, dh=None):
        f = self.root.resolve(path)
        if f is not None and f.is_dir():
            list = f.list()
            for i in list:
                yield i

    @logged
    def access(self, path, flags):
        f = self.root.resolve(path)
        if f is not None:
            return f.access(flags)
        else:
            return -errno.ENOENT

    @logged
    def init_session(self):
        engine = sqlalchemy.create_engine(config.DB['url'], echo=config.DB['echo'])
        if config.DB['type'] == "sqlite":
            engine.execute("PRAGMA foreign_keys=ON")
        elif config.DB['type'] == "postgresql":
            if config.DB['pg_recreate_schema']:
                engine.execute("DROP SCHEMA %s CASCADE;" % (config.DB['schema']))
                engine.execute("CREATE SCHEMA %s;" % (config.DB['schema']))
        Session = orm.sessionmaker(bind=engine)
        Base.metadata.create_all(engine)
        return Session()

    def __repr__(self):
        return 'MorphFS()'
