# Base classes for virtual files

from __future__ import division, unicode_literals, print_function

import os
import errno


class VFile(object):

    def __init__(self, path, type):
        pass

    def resolve(self, path):
        pass

    def attr(self):
        pass

    def access(self, flags):
        """
        Checks access permissions. Permissions are checked separately
        for different access types which are represented by the flag
        parameter.

        Different flag parameters:
        --------------------------
        :os.F_OK: Check if file exists
        :os.R_OK: File is readable
        :os.W_OK: File is writable
        :os.X_OK: File is executable or accessible

        :param flags: The access flag to check for.
        :type flags: int

        :return: 0 on allow, -errno.EACCES otherwise.
        """
        pass

    def readlink(self):
        """
        Get the target of a symlink.

        :return: The symlinks content as byte string or -errno.EOPNOTSUPP
        """
        return -errno.EOPNOTSUPP

    def chmod(self, mode):
        pass

    def chown(self, uid, gid):
        pass


class VPath(object):
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
        p = path
        if p[0] == "/":
            p = p[1: len(p)]
        if p[-1] == "/":
            p = p[0: -1]
        self.__path = p.split("/")

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
        return VPath("/".join(selection))

    def __len__(self):
        return len(self.__path)

    def __str__(self):
        return "/" + "/".join(self.__path)

    def __repr__(self):
        return "<VPath: /" + "/".join(self.__path) + ">"

