#
# This module provides classes that can be used in order to
# implement virtual file systems.
#

from __future__ import division, print_function

import os
import re
import stat
import fuse
import errno
import calendar
from datetime import datetime
from log import logged


class FuseFile(fuse.Direntry):
    """
    Class that represents the concept of a file. As in UNIX file systems
    a file can also represent a directory or link (other types are not supported
    by this class).
    """

    # Directory default size (bytes)
    DIRSIZE = 4096

    def __init__(self, path, mode=0755, uid=0, gid=0, typ=0, ino=0, offset=0):
        self.path = path
        self.mode = mode
        self.uid = uid
        self.gid = gid
        self.type = typ
        self.ino = ino
        self.offset = offset

    #
    # File properties
    #
    @property
    def path(self):
        """The files absolute path"""
        return self.__path

    @path.setter
    def path(self, path):
        self.__path = Path(path)

    @property
    def name(self):
        """The files name"""
        if len(self.path) < 1:
            return "/"
        else:
            return list(self.path)[-1]

    @name.setter
    def name(self, name):
        if len(self.path) > 0 and "/" not in name:
            self.__path[-1] = name

    @property
    def mode(self):
        """The files mode (see unix file modes)"""
        return self.__mode

    @mode.setter
    def mode(self, mode):
        self.__mode = Mode(int(mode))

    @property
    def uid(self):
        """The id of the user that owns the file"""
        return self.__uid

    @uid.setter
    def uid(self, uid):
        self.__uid = uid

    @property
    def gid(self):
        """The id of the group that owns the file"""
        return self.__gid

    @gid.setter
    def gid(self, gid):
        self.__gid = gid

    #
    # File methods
    #
    def resolve(self, path):
        p = Path(str(path))
        if len(p) == 0:
            return self

        else:
            name = list(p)[0]
            found = [f for f in self.list() if f.name == name]
            if len(found) == 1:
                if len(p) == 1:
                    p = Path('/')
                else:
                    p = p[1:]
                return found[0].resolve(p)

        return None

    @logged
    def getattr(self):
        """
        Return a stat object.

        :return: A stat object
        """
        return Stat(st_mode=int(self.mode), st_size=len(self), st_gid=self.gid, st_uid=self.uid)

    @logged
    def access(self, flags):
        """
        Checks access permissions. Permissions are checked separately
        for different access types which are represented by the flag
        parameter.

        Different flag parameters:
        :os.F_OK: Check if file exists
        :os.R_OK: File is readable
        :os.W_OK: File is writable
        :os.X_OK: File is executable or accessible

        :param flags: The access flag to check for.
        :type flags: int

        :return: 0 on allow, -errno.EACCES otherwise.
        """
        return 0

    @logged
    def read(self, size=-1, offset=0):
        """
        Read the content of the file as bytestring.

        :param size: The maximum number of bytes to read or
                     -1 for all data.
        :type size: int
        :param offset: The stat position from where to read the data.
        :type offset: int

        :return: The content of the file.
        """
        return -errno.EOPNOTSUPP

    @logged
    def write(self, buf, offset=0):
        """
        Write data to the file.

        :param buf: The data to write.
        :type buf: str
        :param offset: The position where to start writing.
        :type offset: int

        :return: 0 on success or and negative error code.
        """
        return -errno.EOPNOTSUPP

    @logged
    def list(self):
        """
        If the file is a directory this method lists its content by returning
        a list of File or Direntry objects. This should at least list '..' and '.'
        """
        if self.is_dir():
            return [fuse.Direntry('.'), fuse.Direntry('..')]
        else:
            return -errno.EOPNOTSUPP

    @logged
    def is_dir(self):
        """
        Checks if the file is a directory.

        :return: True if a file, false otherwise.
        """
        return self.mode.is_dir()

    @logged
    def is_file(self):
        """
        Checks if the file is a regular file.

        :return: True if a file, false otherwise.
        """
        return self.mode.is_file()

    @logged
    def is_link(self):
        """
        Checks if the file is a symlink.

        :return: True if a link, false otherwise.
        """
        return self.mode.is_link()

    def __len__(self):
        """
        Determine the size of the file.
        """
        if self.is_dir():
            return self.DIRSIZE
        else:
            data = self.read()
            if data == -errno.EOPNOTSUPP:
                length = 0
            else:
                length = len(data)
            return length

    def __str__(self):
        return str(self.path)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, str(self.path))


class Path(object):
    """
    A path class, that represents the path as an immutable
    collection of strings. Supported operations are
    """

    def __init__(self, path=""):
        """
        Initializes the path with a string.

        :param path: A path as a string.
        :type path: str|unicode
        """
        p = str(path)
        if p[0] == "/":
            p = p[1: len(p)]
        if len(p) > 1 and p[-1] == "/":
            p = p[0: -1]
        self.__path = [i for i in p.split("/") if i != ""]

    def __getitem__(self, index):
        """
        Access parts of the path.

        :param index: The index a integer or a slice object (start:end:step).
        :type index: int|slice

        :return: A VPath object that represents the selected
        part of the path.
        """
        if type(index) == int:
            selection = [self.__path[index]]
        else:
            selection = self.__path[index]
        return Path("/".join(selection))

    def __setitem__(self, key, value):
        self.__path[key] = value

    def __add__(self, other):
        list_self = list(self)
        list_other = list(Path(other))
        return Path("/".join(list_self + list_other))

    def __len__(self):
        return len(self.__path)

    def __str__(self):
        return "/" + "/".join(self.__path)

    def __repr__(self):
        return "Path(%s)" % (str(self))

    def __iter__(self):
        return iter(self.__path)


class Stat(fuse.Stat):
    """
    Stat class with some comfort functions and useful defaults.
    """

    def __init__(self, st_mode, st_size, st_nlink=1, st_uid=None, st_gid=None,
                 dt_atime=None, dt_mtime=None, dt_ctime=None):
        """
        Initialize the stat object

        :param st_mode: The file system mode.
        :param st_size: The size of the file.
        :param st_nlink: The number of hardlinks pointing to the file (default 1)
        :param st_uid: The id of the owner.
        :param st_gid: the id of the owning group.
        :param dt_atime: The access time.
        :param dt_mtime: The modification time.
        :param dt_ctime: The creation time.
        """
        self.st_mode = st_mode
        self.st_size = st_size
        self.st_nlink = st_nlink
        self.st_uid = st_uid if st_uid is not None else os.getuid()
        self.st_gid = st_gid if st_gid is not None else os.getgid()
        now = datetime.utcnow()
        self.dt_atime = dt_atime or now
        self.dt_mtime = dt_mtime or now
        self.dt_ctime = dt_ctime or now

    @property
    def st_ino(self):
        return 0

    @property
    def st_dev(self):
        return 0

    @property
    def dt_atime(self):
        return datetime.utcfromtimestamp(self.st_atime)

    @dt_atime.setter
    def dt_atime(self, time):
        self.st_atime = calendar.timegm(time.timetuple())

    @property
    def dt_ctime(self):
        return datetime.utcfromtimestamp(self.st_ctime)

    @dt_ctime.setter
    def dt_ctime(self, time):
        self.st_ctime = calendar.timegm(time.timetuple())

    @property
    def dt_mtime(self):
        return datetime.utcfromtimestamp(self.st_mtime)

    @dt_mtime.setter
    def dt_mtime(self, time):
        self.st_mtime = calendar.timegm(time.timetuple())

    def __repr__(self):
        return "Stat(st_mode=%s, st_uid=%i, st_gid=%i)" % (str(Mode(self.st_mode)), self.st_uid, self.st_gid)


class Mode(object):
    """
    A class that represents file modes as int or (e.g. 0777) as
    string (-rwx-rx-rx).
    """

    CPATTERN = re.compile(r"^[df\-][r\-][w\-][x\-][r\-][w\-][x\-][r\-][w\-][x\-]$")

    def __init__(self, mode="-rwxr-xr-x"):
        """
        Creates a new mode object

        :param mode: The modes as sting (e.g. 'drwxrwxrwx') or integer
        :type mode: int|str
        """
        if type(mode) == str:
            self.__mode = self.mode_from_str(mode)
        else:
            self.__mode = mode

    def is_file(self):
        """
        Checks if the stats represent a regular file.

        :return: True if a file, false otherwise.
        """
        return (self.__mode & stat.S_IFREG) > 0

    def is_dir(self):
        """
        Checks if the stats represent a directory.

        :return: True if a directory, false otherwise.
        """
        return (self.__mode & stat.S_IFDIR) > 0

    def is_link(self):
        """
        Checks if the stats represent a symlink.

        :return: True if a link, false otherwise.
        """
        return (self.__mode & stat.S_IFLNK) > 0

    #
    # built in methods
    #
    def __int__(self):
        return self.__mode

    def __str__(self):
        return self.mode_to_string(self.__mode)

    def __repr__(self):
        return "Mode(%s)" % (str(self))

    #
    # static methods
    #
    @staticmethod
    def mode_from_str(strmode):
        """
        Converts a mode from string to int.

        :param strmode: The mode represented as string
        :type strmode: str

        :return: The mode as integer
        """
        mode = 0
        # validate
        if re.match(Mode.CPATTERN, strmode) is None:
            raise TypeError("Invalid mode string: " + strmode)
            # file type
        if strmode[0] == "-":
            mode |= stat.S_IFREG
        elif strmode[0] == "d":
            mode |= stat.S_IFDIR
        elif strmode[0] == "l":
            mode |= stat.S_IFLNK
            # user rights
        if strmode[1] == "r":
            mode |= stat.S_IRUSR
        if strmode[2] == "w":
            mode |= stat.S_IWUSR
        if strmode[3] == "x":
            mode |= stat.S_IXUSR
            # group rights
        if strmode[4] == "r":
            mode |= stat.S_IRGRP
        if strmode[5] == "w":
            mode |= stat.S_IWGRP
        if strmode[6] == "x":
            mode |= stat.S_IXGRP
            # others rights
        if strmode[7] == "r":
            mode |= stat.S_IROTH
        if strmode[8] == "w":
            mode |= stat.S_IWOTH
        if strmode[9] == "x":
            mode |= stat.S_IXOTH

        return mode

    @staticmethod
    def mode_to_string(mode):
        """
        Convert the mode from int to a string representation.

        :param mode: The mode as integer
        :type mode: int

        :return: A string representation of the mode
        """
        listmode = list("----------")
        # file type
        if mode & stat.S_IFLNK:
            listmode[0] = "l"
        elif mode & stat.S_IFDIR:
            listmode[0] = "d"
            # user rights
        if mode & stat.S_IRUSR:
            listmode[1] = "r"
        if mode & stat.S_IWUSR:
            listmode[2] = "w"
        if mode & stat.S_IXUSR:
            listmode[3] = "x"
            # group rights
        if mode & stat.S_IRGRP:
            listmode[4] = "r"
        if mode & stat.S_IWGRP:
            listmode[5] = "w"
        if mode & stat.S_IXGRP:
            listmode[6] = "x"
            # others rights
        if mode & stat.S_IROTH:
            listmode[7] = "r"
        if mode & stat.S_IWOTH:
            listmode[8] = "w"
        if mode & stat.S_IXOTH:
            listmode[9] = "x"
        return "".join(listmode)
