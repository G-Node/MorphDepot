import fuse
import errno
from log import logged


class DefaultFS(object):

    @logged
    def __init__(self):
        pass

    @logged
    def fsinit(self):
        return 0

    @logged
    def fsdestroy(self):
        return 0

    @logged
    def statfs(self):
        return fuse.StatVfs()

    @logged
    def getattr(self, path):
        return -errno.ENOENT

    @logged
    def utime(self, path, times):
        atime, mtime = times
        return self.utimes(path, atime, mtime)

    @logged
    def utimes(self, path, atime, mtime):
        return -errno.EOPNOTSUPP

    @logged
    def access(self, path, flags):
        return -errno.EACCES

    @logged
    def readlink(self, path):
        return -errno.EOPNOTSUPP

    @logged
    def mknod(self, path, mode, rdev):
        return -errno.EOPNOTSUPP

    @logged
    def mkdir(self, path, mode):
        return -errno.EOPNOTSUPP

    @logged
    def unlink(self, path):
        return -errno.EOPNOTSUPP

    @logged
    def rmdir(self, path):
        return -errno.EOPNOTSUPP

    @logged
    def symlink(self, target, name):
        return -errno.EOPNOTSUPP

    @logged
    def link(self, target, name):
        return -errno.EOPNOTSUPP

    @logged
    def rename(self, oldname, newname):
        return -errno.EOPNOTSUPP

    @logged
    def chmod(self, path, mode):
        return -errno.EOPNOTSUPP

    @logged
    def chown(self, path, uid, gid):
        return -errno.EOPNOTSUPP

    @logged
    def truncate(self, path, size):
        return -errno.EOPNOTSUPP

    @logged
    def opendir(self, path):
        if path == "/":
            return 0
        else:
            return -errno.EACCES








