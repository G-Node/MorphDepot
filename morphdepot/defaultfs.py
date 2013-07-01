"""

this module is partially based on TemplateFS
http://bazaar.launchpad.net/~mgiuca/fuse-python-docs/trunk/view/head:/templatefs.py

"""
import fuse
import errno
from log import logged


class DefaultFS(fuse.Fuse):
    """
    A default Fuse filesystem object. Implements methods which are called by the 
    Fuse system as a result of the operating system requesting filesystem
    operations on places where this file system is mounted.

    Unless otherwise documented, all of these methods return an int.
    This should be 0 on success, or the NEGATIVE of an errno value on failure.
    For example, to report "no such file or directory", methods return
    -errno.ENOENT. See the errno manpage for a list of errno values. (Though
    note that Python's errno is slightly different; see help(errno)).
    Methods should return errno.EOPNOTSUPP (operation not supported) if they
    are deliberately not supported, or errno.ENOSYS (function not implemented)
    if they have not yet been implemented.

    Unless otherwise documented, all paths should begin with a '/' and be
    "absolute paths", where "absolute" means relative to the root of the
    mounted filesystem. There are no references to files outside the
    filesystem.
    """

    @logged
    def __init__(self, *args, **kwargs):
        """
        Creates a new TemplateFS object. Needs to call fuse.Fuse.__init__ with
        the args (just forward them along). Note that options passed to the
        filesystem through the command line are not available during the
        execution of this method.

        If parsing the command line argument fails, fsdestroy is called
        without prior calling fsinit.
        """
        super(DefaultFS, self).__init__(*args, **kwargs)

    @logged
    def fsinit(self):
        """
        Will be called after the command line arguments are successfully
        parsed. It doesn't have to exist or do anything, but as options to the
        filesystem are not available in __init__, fsinit is more suitable for
        the mounting logic than __init__.

        To access the command line passed options and nonoption arguments, use
        cmdline.

        The mountpoint is not stored in cmdline.
        """
        pass

    @logged
    def fsdestroy(self):
        """
        Will be called when the file system is about to be unmounted.
        It doesn't have to exist, or do anything.
        """
        pass

    @logged
    def statfs(self):
        """
        Retrieves information about the mounted filesystem.
        Returns a fuse.StatVfs object containing the details.
        This is optional. If omitted, Fuse will simply report a bunch of 0s.

        The StatVfs should have the same fields as described in man 2 statfs
        (Linux Programmer's Manual), except for f_type.
        This includes the following:
            f_bsize     (optimal transfer block size)
            f_blocks    (number of blocks total)
            f_bfree     (number of free blocks)
            f_bavail    (number of free blocks available to non-root)
            f_files     (number of file nodes in system)
            f_ffree     (number of free file nodes)
            f_namemax   (max length of filenames)

        Note f_type, f_frsize, f_favail, f_fsid and f_flag are ignored.
        """
        return fuse.StatVfs()

    @logged
    def getattr(self, path):
        """
        Retrieves information about a file (the "stat" of a file).
        Returns a fuse.Stat object containing details about the file or
        directory.
        Returns -errno.ENOENT if the file is not found, or another negative
        errno code if another error occurs.
        """
        return -errno.ENOENT

    @logged
    def utime(self, path, times):
        """
        Sets the access and modification times on a file.
        times: (atime, mtime) pair. Both ints, in seconds since epoch.
        Deprecated in favour of utimens.
        """
        atime, mtime = times
        return self.utimes(path, atime, mtime)

    @logged
    def utimes(self, path, atime, mtime):
        """
        Sets the access and modification times on a file, in nanoseconds.
        atime, mtime: Both fuse.TimeSpec objects, with 'tv_sec' and 'tv_nsec'
        attributes, which are the seconds and nanoseconds parts, respectively.
        """
        return -errno.EOPNOTSUPP

    @logged
    def access(self, path, flags):
        """
        Checks permissions for accessing a file or directory.
        flags: As described in man 2 access (Linux Programmer's Manual).
        Either os.F_OK (test for existence of file), or ORing of os.R_OK, 
        os.W_OK, os.X_OK (test if file is readable, writable and executable, 
        respectively. Must pass all tests).

        Should return 0 for "allowed", or -errno.EACCES if disallowed.
        May not always be called. For example, when opening a file, open may
        be called and access avoided.
        """
        return -errno.EACCES

    @logged
    def readlink(self, path):
        """
        Get the target of a symlink.
        Returns a bytestring with the contents of a symlink (its target).
        May also return an int error code.
        """
        return -errno.EOPNOTSUPP

    @logged
    def mknod(self, path, mode, rdev):
        """
        Creates a non-directory file (or a device node).
        mode: Unix file mode flags for the file being created.
        rdev: Special properties for creation of character or block special
              devices (I've never gotten this to work).
              Always 0 for regular files or FIFO buffers.
        """
        # Note: mode & 0770000 gives you the non-permission bits.
        # Common ones:
        # S_IFREG:  0100000 (A regular file)
        # S_IFIFO:  010000  (A fifo buffer, created with mkfifo)

        # Potential ones (I have never seen them):
        # Note that these could be made by copying special devices or sockets
        # or using mknod, but I've never gotten FUSE to pass such a request
        # along.
        # S_IFCHR:  020000  (A character special device, created with mknod)
        # S_IFBLK:  060000  (A block special device, created with mknod)
        # S_IFSOCK: 0140000 (A socket, created with mkfifo)

        # Also note: You can use self.GetContext() to get a dictionary
        #   {'uid': ?, 'gid': ?}, which tells you the uid/gid of the user
        #   executing the current syscall. This should be handy when creating
        #   new files and directories, because they should be owned by this
        #   user/group.
        return -errno.EOPNOTSUPP

    @logged
    def mkdir(self, path, mode):
        """
        Creates a directory.
        mode: Unix file mode flags for the directory being created.
        """
        # Note: mode & 0770000 gives you the non-permission bits.
        # Should be S_IDIR (040000); I guess you can assume this.
        # Also see note about self.GetContext() in mknod.
        return -errno.EOPNOTSUPP

    @logged
    def unlink(self, path):
        """
        Deletes a file.
        """
        return -errno.EOPNOTSUPP

    @logged
    def rmdir(self, path):
        """
        Deletes a directory.
        """
        return -errno.EOPNOTSUPP

    @logged
    def symlink(self, target, name):
        """
        Creates a symbolic link from path to target.

        The 'name' is a regular path like any other method (absolute, but
        relative to the filesystem root).
        The 'target' is special - it works just like any symlink target. It
        may be absolute, in which case it is absolute on the user's system,
        NOT the mounted filesystem, or it may be relative. It should be
        treated as an opaque string - the filesystem implementation should not
        ever need to follow it (that is handled by the OS).

        Hence, if the operating system creates a link FROM this system TO
        another system, it will call this method with a target pointing
        outside the filesystem.
        If the operating system creates a link FROM some other system TO this
        system, it will not touch this system at all (symlinks do not depend
        on the target system unless followed).
        """
        return -errno.EOPNOTSUPP

    @logged
    def link(self, target, name):
        """
        Creates a hard link from name to target. Note that both paths are
        relative to the mounted file system. Hard-links across systems are not
        supported.
        """
        return -errno.EOPNOTSUPP

    @logged
    def rename(self, oldname, newname):
        """
        Moves a file from old to new. (old and new are both full paths, and
        may not be in the same directory).
        
        Note that both paths are relative to the mounted file system.
        If the operating system needs to move files across systems, it will
        manually copy and delete the file, and this method will not be called.
        """
        return -errno.EOPNOTSUPP

    @logged
    def chmod(self, path, mode):
        """
        Changes the mode of a file or directory.
        """
        return -errno.EOPNOTSUPP

    @logged
    def chown(self, path, uid, gid):
        """
        Changes the owner of a file or directory.
        """
        return -errno.EOPNOTSUPP

    @logged
    def truncate(self, path, size):
        """
        Shrink or expand a file to a given size.
        If 'size' is smaller than the existing file size, truncate it from the
        end. If 'size' if larger than the existing file size, extend it with 
        null bytes.
        """
        return -errno.EOPNOTSUPP

    #---------------------------------------------------------------------------
    # DIRECTORY OPERATION METHODS
    #---------------------------------------------------------------------------

    @logged
    def opendir(self, path):
        """
        Checks permissions for listing a directory.
        This should check the 'r' (read) permission on the directory.

        On success, *may* return an arbitrary Python object, which will be
        used as the "fh" argument to all the directory operation methods on
        the directory. Or, may just return None on success.
        On failure, should return a negative errno code.
        Should return -errno.EACCES if disallowed.
        """
        if path == "/":
            return 0
        else:
            return -errno.EACCES

    @logged
    def releasedir(self, path, dh=None):
        """
        Closes an open directory. Allows filesystem to clean up.
        """
        pass

    @logged
    def fsyncdir(self, path, datasync, dh=None):
        """
        Synchronises an open directory.
        datasync: If True, only flush user data, not metadata.
        """
        pass

    @logged
    def readdir(self, path, offset, dh=None):
        """
        Generator function. Produces a directory listing.
        Yields individual fuse.Direntry objects, one per file in the
        directory. Should always yield at least "." and "..".
        Should yield nothing if the file is not a directory or does not exist.
        (Does not need to raise an error).

        offset: I don't know what this does, but I think it allows the OS to
        request starting the listing partway through (which I clearly don't
        yet support). Seems to always be 0 anyway.
        """
        if path == "/":
            yield fuse.Direntry(".")
            yield fuse.Direntry("..")

    #---------------------------------------------------------------------------
    # FILE OPERATION METHODS
    #---------------------------------------------------------------------------

    @logged
    def open(self, path, flags):
        """
        Open a file for reading/writing, and check permissions.
        flags: As described in man 2 open (Linux Programmer's Manual).
               ORing of several access flags, including one of os.O_RDONLY,
               os.O_WRONLY or os.O_RDWR. All other flags are in os as well.

        On success, *may* return an arbitrary Python object, which will be
        used as the "fh" argument to all the file operation methods on the
        file. Or, may just return None on success.
        On failure, should return a negative errno code.
        Should return -errno.EACCES if disallowed.
        """
        return -errno.EOPNOTSUPP

    @logged
    def create(self, path, mode, rdev):
        """
        Creates a file and opens it for writing.
        Will be called in favour of mknod+open, but it's optional (OS will
        fall back on that sequence).
        mode: Unix file mode flags for the file being created.
        rdev: Special properties for creation of character or block special
              devices (I've never gotten this to work).
              Always 0 for regular files or FIFO buffers.
        See "open" for return value.
        """
        return -errno.EOPNOTSUPP

    @logged
    def fgetattr(self, path, fh=None):
        """
        Retrieves information about a file (the "stat" of a file).
        Same as Fuse.getattr, but may be given a file handle to an open file,
        so it can use that instead of having to look up the path.
        """
        return self.getattr(path)

    @logged
    def release(self, path, flags, fh=None):
        """
        Closes an open file. Allows filesystem to clean up.
        flags: The same flags the file was opened with (see open).
        """
        pass

    @logged
    def fsync(self, path, datasync, fh=None):
        """
        Synchronises an open file.
        datasync: If True, only flush user data, not metadata.
        """
        pass

    @logged
    def flush(self, path, fh=None):
        """
        Flush cached data to the file system.
        This is NOT an fsync (I think the difference is fsync goes both ways,
        while flush is just one-way).
        """
        pass

    @logged
    def read(self, path, size, offset, fh=None):
        """
        Get all or part of the contents of a file.
        size: Size in bytes to read.
        offset: Offset in bytes from the start of the file to read from.
        Does not need to check access rights (operating system will always
        call access or open first).
        Returns a byte string with the contents of the file, with a length no
        greater than 'size'. May also return an int error code.

        If the length of the returned string is 0, it indicates the end of the
        file, and the OS will not request any more. If the length is nonzero,
        the OS may request more bytes later.
        To signal that it is NOT the end of file, but no bytes are presently
        available (and it is a non-blocking read), return -errno.EAGAIN.
        If it is a blocking read, just block until ready.
        """
        return -errno.EOPNOTSUPP

    @logged
    def write(self, path, buf, offset, fh=None):
        """
        Write over part of a file.
        buf: Byte string containing the text to write.
        offset: Offset in bytes from the start of the file to write to.
        Does not need to check access rights (operating system will always
        call access or open first).
        Should only overwrite the part of the file from offset to
        offset+len(buf).

        Must return an int: the number of bytes successfully written (should
        be equal to len(buf) unless an error occured). May also be a negative
        int, which is an errno code.
        """
        return -errno.EOPNOTSUPP

    @logged
    def ftruncate(self, path, size, fh=None):
        """
        Shrink or expand a file to a given size.
        Same as Fuse.truncate, but may be given a file handle to an open file,
        so it can use that instead of having to look up the path.
        """
        return -errno.EOPNOTSUPP






