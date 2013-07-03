
from fuse import Direntry
from log import logged
from fshelper import File, Path


class RootDir(File):

    def __init__(self):
        super(RootDir, self).__init__("/", "/")

    @logged
    def list(self):
        return [Direntry("."), Direntry(".."), Direntry("scientists"),
                Direntry("experiments"), Direntry("options")]

    @logged
    def resolve(self, path):
        p = Path(str(path))
        result = None
        if len(p) == 0:
            result = self
        else:
            name = p[0]
            found = [f for f in self.list() if f.name == name]
            if len(found) == 1:
                result = found[0]
        return result


