import os

from sqlalchemy.orm.session import Session

import stat
from fuse import Direntry
from log import logged
from fshelper import FuseFile, Path, Stat
from serializer import Serializer
from models.core import Scientist, Experiment, TissueSample, Protocol, Neuron, File, Animal

#-------------------------------------------------------------------------------
# HELPER CLASSES
#-------------------------------------------------------------------------------

class ModelFile(FuseFile):
    """
    abstract class that implements initialization from an object for files.
    """
    def __init__(self, path, obj, *args, **kwargs):
        """
        Initialize a new virtual file / folder from a given object.

        :param path:    an absolute path 'above' this object.
        :param obj:     an instance of a certain model.
        """
        self.model_instance = obj

        if not kwargs.has_key('mode'):
            kwargs['mode'] = stat.S_IFREG | 0755

        # TODO add permissions resolution

        name = str(obj.__str__())
        path = os.path.join(path, name)

        super(ModelFile, self).__init__(path, name, *args, **kwargs)

    def getattr(self):
        kwargs = {}
        kwargs['st_mode'] = int(self.mode)
        kwargs['st_size'] = len(self)
        kwargs['st_gid'] = self.gid
        kwargs['st_uid'] = self.uid
        kwargs['dt_mtime'] = self.model_instance.mtime
        kwargs['dt_ctime'] = self.model_instance.ctime

        return Stat( **kwargs )


class ModelDir(ModelFile):
    """
    abstract class that implements initialization from an object for folders.
    """
    def __init__(self, path, obj, *args, **kwargs):
        kwargs['mode'] = stat.S_IFDIR | 0755
        super(ModelDir, self).__init__(path, obj, *args, **kwargs)


#-------------------------------------------------------------------------------
# STATIC FOLDERS
#-------------------------------------------------------------------------------

class RootDir(FuseFile):
    """
    It's a static root folder with 'scientists' folder inside.
    """

    def __init__(self, session):
        self.session = session
        mode = stat.S_IFDIR | 0755
        super(RootDir, self).__init__("/", name="/", mode=mode)

    @logged
    def list(self):
        return [Direntry("."), Direntry(".."), Scientists(self.session)]


class Scientists(FuseFile):
    """
    It's a static folder in the root dir that contains all scientists.
    """
    def __init__(self, session):
        self.session = session
        mode = stat.S_IFDIR | 0755
        super(Scientists, self).__init__(path="/scientists", name="scientists", mode=mode)

    @logged
    def list(self):
        """
        Scientists folder contains all registered scientists.

        :return:        a list of scientist folders.
        """
        contents = [Direntry("."), Direntry("..")]
        for sct in self.session.query(Scientist):
            contents.append(ScientistDir(self.path.__str__(), sct))

        return contents


#-------------------------------------------------------------------------------
# MODEL FOLDERS
#-------------------------------------------------------------------------------

class ScientistDir(ModelDir):
    """
    Class represents a Scientist folder.
    """

    @logged
    def list(self):
        """
        Scientist folder contains:
        - information about the scientist as info.yaml
        - folders with all experiments, made by this scientist

        :return:        a list of files and folders.
        """
        contents = []

        # 1. info.yaml with attributes
        info = ModelInfo(self.path.__str__(), self.model_instance)
        contents.append(info)

        # 2. list of experiments
        session = Session.object_session(self.model_instance)
        experiments = session.query(Experiment).filter( \
            Experiment.scientist_id == str(self.model_instance.id))
        for exp in experiments:
            contents.append(ExperimentDir(self.path.__str__(), exp))

        return contents


class ExperimentDir(ModelDir):
    """
    Class represents an Experiment folder.
    """

    @logged
    def list(self):
        """
        Experiment folder contains:
        - information about the experiment as info.yaml
        - folders with all related tissue samples

        :return:        a list of files and folders.
        """
        contents = []

        # 1. info.yaml with attributes
        info = ModelInfo(self.path.__str__(), self.model_instance)
        contents.append(info)

        # 2. list of experiments
        session = Session.object_session(self.model_instance)
        objs = session.query(TissueSample).filter( \
            TissueSample.experiment_id == self.model_instance.id)
        for obj in objs:
            contents.append(TissueSampleDir(self.path.__str__(), obj))

        return contents

#-------------------------------------------------------------------------------
# FILES
#-------------------------------------------------------------------------------

class ModelInfo(ModelFile):
    """
    Class represents a info.yaml file with properties of an instance of a 
    certain model.
    """
    def __init__(self, path, obj, *args, **kwargs):
        super(ModelInfo, self).__init__(path, obj, *args, **kwargs)
        self.name = 'info.yaml'
        self.path = os.path.join(path, self.name)

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

