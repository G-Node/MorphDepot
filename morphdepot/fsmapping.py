import os

import stat
from fuse import Direntry
from log import logged
from fshelper import File, Path
from serializer import Serializer


class RootDir(File):

    def __init__(self):
        mode = stat.S_IFDIR | 0755
        super(RootDir, self).__init__(path="/", name="/", mode=mode)

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


class ModelResolver(object):
    """
    abstract class that implements initialization and a generic path resolution 
    for virtual file system objects.
    """
    def __init__(self, path, obj, *args, **kwargs):
        """
        Initialize a new virtual file / folder from a given object.

        :param path:    an absolute path 'above' this object.
        :param obj:     an instance of a certain model.
        """
        self.model_instance = obj

        if obj.__class__.__name__.lower() in ['scientist', 'experiment', \
            'tissuesample', 'microscopeimage', 'microscopeimagestack', \ 
                'segmentation']:
            kwargs['mode'] = 'drwxr-xr-x'

        else:
            kwargs['mode'] = '-rwxr-xr-x'

        # TODO add permissions resolution

        path = os.path.join(path, obj.__str__())
        name = obj.__str__()

        super(ModelResolver, self).__init__(path, name, *args, **kwargs)

    @logged
    def resolve(self, path):
        p = Path(str(path))
        if len(p) == 0:
            return self

        else:
            name = p[0]
            found = [f for f in self.list() if f.name == name]
            if len(found) == 1:
                return found[0].resolve("/" + "/".join( p[1:] ))

        return None

#-------------------------------------------------------------------------------
# FOLDERS
#-------------------------------------------------------------------------------


class ScientistDir(File, ModelResolver):
    """
    Class represents a Scientist folder.
    """

    @logged
    def list(self):
        """
        Scientist folder contains:
        - information about the scientist
        - folders with all experiments, made by this scientist

        :return:        a list of files and folders.
        """
        contents = []

        # 1. info.yaml with scientist attributes
        info = ModelInfo(self.path, self.model_instance)
        contents.append(info)

        # 2. list of experiments
        session = Session.object_session(self.model_instance)
        experiments = session.query(Experiment).filter( \
            Experiment.scientist_id == self.model_instance.id)
        for exp in experiments:
            contents.append(ExperimentDir(self.path, exp))

        return contents


class ExperimentDir(File, ModelResolver):
    """
    Class represents an Experiment folder.
    """

    @logged
    def list(self):
        raise NotImplementedError

#-------------------------------------------------------------------------------
# FILES
#-------------------------------------------------------------------------------


class ModelInfo(File, ModelResolver):
    """
    Class represents a info.yaml file with properties of an instance of a 
    certain model.
    """

    def read(self):
        """
        Returns an attached object representation as YAML file (bytestring).
        """
        return Serializer.serialize(self.model_instance) # binary?

    def write(self, buf):
        """
        Updates object information 

        :param buf:     a YAML representation of an object.
        :type buf:      str

        :return:        0 on success or and negative error code.
        """
        try:
            new = Serializer.deserialize(self.model_instance.__class__, buf)
            new.id = self.model_instance.id

        except Exception, e:
            return -1 # TODO find a way to handle expceptions better..

        session = Session.object_session(self.model_instance)
        session.merge(new)
        session.commit() # needed?

        return 0

