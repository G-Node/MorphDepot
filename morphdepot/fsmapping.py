from fuse import Direntry
from fshelper import File

class RootDir(File):

    def __init__(self):
        super(RootDir, self).__init__("/", "/")

    def list(self):
        return [Direntry("."), Direntry(".."), Direntry("scientists"),
                Direntry("experiments"), Direntry("options")]

    def resolve(self, path):
        pass
