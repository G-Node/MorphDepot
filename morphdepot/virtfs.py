# Base classes for morphfs

from __future__ import division, unicode_literals, print_function

import os
import re
import stat
import fuse
import calendar
from datetime import datetime


class Stat(fuse.Stat):
    """
    Stat class with some comfort functions
    """

    def __init__(self, st_mode, st_size, st_nlink=1, st_uid=None, st_gid=None,
                 dt_atime=None, dt_mtime=None, dt_ctime=None):
        """

        :param st_mode:
        :param st_size:
        :param st_nlink:
        :param st_uid:
        :param st_gid:
        :param dt_atime:
        :param dt_mtime:
        :param dt_ctime:
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
    def st_atime(self):
        return datetime.utcfromtimestamp(self.__st_atime)

    @st_atime.setter
    def st_atime(self, time):
        self.__st_atime = calendar.timegm(time.timetuple())

    @property
    def st_ctime(self):
        return datetime.utcfromtimestamp(self.__st_ctime)

    @st_ctime.setter
    def st_ctime(self, time):
        self.__st_ctime = calendar.timegm(time.timetuple())

    @property
    def st_mtime(self):
        return datetime.utcfromtimestamp(self.__st_mtime)

    @st_mtime.setter
    def st_mtime(self, time):
        self.__st_mtime = calendar.timegm(time.timetuple())


class Mode(object):

    CPATTERN = re.compile(r"^[df\-][r\-][w\-][x\-][r\-][w\-][x\-][r\-][w\-][x\-]$")

    def __init__(self, mode="-rwxr-xr-x"):
        if type(mode) == str:
            self.__mode = self.mode_from_str(mode)
        else:
            self.__mode = mode

    def __int__(self):
        return self.__mode

    def __str__(self):
        return self.mode_to_string(self.__mode)

    @staticmethod
    def mode_from_str(strmode):
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
