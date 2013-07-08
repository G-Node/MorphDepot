#from __future__ import division, unicode_literals, print_function

import os
import errno
import yaml
import stat

from sqlalchemy.orm.session import Session
from fuse import Direntry
from log import logged
from fshelper import FuseFile, Path, Stat
from serializer import Serializer
from models.core import Scientist, Experiment, TissueSample, Protocol, Neuron, File, Animal
from models.morph import MicroscopeImage, MicroscopeImageStack, Segmentation
from models.dimensions import AnimalSpecies

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

        :param path:    an absolute path for a given object.
        :type path:     str or a Path instance.
        :param obj:     an instance of a certain model.
        """
        self.model_instance = obj

        # TODO add permissions resolution

        super(ModelFile, self).__init__(path, *args, **kwargs)

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
        super(RootDir, self).__init__("/", mode=mode)

    @logged
    def list(self):
        return [Direntry("."), Direntry(".."), Scientists(self.session),
                DimensionFile("/spec.yml", self.session, AnimalSpecies)]


class Scientists(FuseFile):
    """
    It's a static folder in the root dir that contains all scientists.
    """
    def __init__(self, session):
        self.session = session
        mode = stat.S_IFDIR | 0755
        super(Scientists, self).__init__(path="/scientists", mode=mode)

    @logged
    def list(self):
        """
        Scientists folder contains all registered scientists.

        :return:        a list of scientist folders.
        """
        contents = [Direntry("."), Direntry("..")]
        for sct in self.session.query(Scientist):
            contents.append(ScientistDir(self.path + str(sct), sct))

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
        contents = [Direntry("."), Direntry("..")]

        # 1. info.yaml with attributes
        info = ModelInfo(self.path + 'info.yaml', self.model_instance)
        contents.append(info)

        # 2. list of experiments
        session = Session.object_session(self.model_instance)
        experiments = session.query(Experiment).filter( \
            Experiment.scientist_id == str(self.model_instance.id))
        for exp in experiments:
            contents.append(ExperimentDir(self.path + str(exp), exp))

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
        contents = [Direntry("."), Direntry("..")]

        # 1. info.yaml with attributes
        info = ModelInfo(self.path + 'info.yaml', self.model_instance)
        contents.append(info)

        # 2. list of experiments
        session = Session.object_session(self.model_instance)
        objs = session.query(TissueSample).filter( \
            TissueSample.experiment_id == self.model_instance.id)
        for obj in objs:
            contents.append(TissueSampleDir(self.path + str(obj), obj))

        return contents


class TissueSampleDir(ModelDir):
    """
    Class represents a Tissue Sample folder.
    """
    @logged
    def list(self):
        """
        Tissue Sample folder contains:
        - information about the sample as info.yaml
        - animal information as animal.yaml
        - 'images' folder with image files
        - 'image_stacks' folder with image stacks
        - 'segmentations' folder with segmentations
        - 'electrophysiology' folder with ephys data?
        - 'neurons' folder with neurons analyzed in the scope of this sample

        :return:        a list of files and folders.
        """
        contents = [Direntry("."), Direntry("..")]

        # 1. info.yaml with attributes
        info = ModelInfo(self.path + 'info.yaml', self.model_instance)
        contents.append(info)
        # TODO info.yaml should contain link to the Protocol!

        # 2. animal.yaml with Animal description
        info = AnimalInfo(self.path + 'animal.yaml', self.model_instance.animal)
        contents.append(info)

        # 3. 'neurons' folder with neuron descriptions
        info = Neurons(self.path + 'neurons', self.model_instance)
        contents.append(info)

        # 4. list of static folders for raw / processed data
        static_descriptor = {
            'images': MicroscopeImage,
            'image_stacks': MicroscopeImageStack,
            'segmentations': Segmentation
        }
        for staticname, cls in static_descriptor.items():
            staticdir = TSStaticDir(self.path + staticname, cls, self.model_instance)
            contents.append(staticdir)

        return contents


class Neurons(ModelDir):
    """
    It's a static folder inside a certain Tissue Sample that contains all 
    neuronal descriptions, investigated within this sample.
    """
    @logged
    def list(self):
        """
        Neurons for a certain Tissue Sample.

        :return:        a list of neuron files.
        """
        contents = [Direntry("."), Direntry("..")]
        for nr in self.model_instance.neuro_representations:
            for neuron in nr.neurons:
                contents.append(NeuronInfo(self.path + str(neuron), neuron))

        return contents


class TSStaticDir(FuseFile):
    """
    It's a static folder in the Tissue Sample that contains all elements of a
    certain type: images, image stacks, segmentations, ephys.
    """
    def __init__(self, path, model, parent):
        self.model = model
        self.parent = parent

        mode = stat.S_IFDIR | 0755
        super(TSStaticDir, self).__init__(path, mode=mode)

    @logged
    def list(self):
        """
        Contains all related objects of the type self.model.

        :return:        a list of folders.
        """
        contents = [Direntry("."), Direntry("..")]

        session = Session.object_session(self.parent)
        q = self.session.query(self.model)
        for obj in q.filter(self.model.tissue_sample == self.parent):
            objdir = NeuroRepresentationDir(self.path + str(obj), obj)
            contents.append(objdir)

        return contents


class NeuroRepresentationDir(ModelDir):
    """
    Class represents a generic NeuroRepresentation folder (can represent a 
    single Image, Image Stack, Segmentation, or Ephys dataset.
    """
    @logged
    def list(self):
        """
        Neuro Representation folder contains:
        - information about the specific representation as info.yaml
        - all files related to this representation

        :return:        a list of files.
        """
        contents = [Direntry("."), Direntry("..")]

        # 1. info.yaml with attributes
        info = ModelInfo(self.path + 'info.yaml', self.model_instance)
        contents.append(info)
        # TODO display neuron connection inside the file!

        # 2. list of all related Files
        for f in self.model_instance.files:
            contents.append(NormalFile(self.path + str(f), f))

        return contents


#-------------------------------------------------------------------------------
# FILES
#-------------------------------------------------------------------------------

class NormalFile(ModelFile):
    pass


class AnimalInfo(ModelFile):
    pass


class NeuronInfo(ModelFile):
    pass


class ModelInfo(ModelFile):
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


class DimensionFile(FuseFile):

    def __init__(self, path, session, dimension, name=None):
        mode = stat.S_IFREG | 0755
        super(DimensionFile, self).__init__(path, mode=mode)
        self.__session = session
        self.__dimension = dimension

    @property
    def dimension(self):
        return self.__dimension

    @property
    def session(self):
        return self.__session

    @logged
    def read(self, size=-1, offset=0):
        dimlist = self.session.query(self.dimension).all()
        dimdict = dict()
        for d in dimlist:
            dimdict[str(d.name)] = {str("description"): str(d.description), str("comment"): str(d.comment)}
        return str(yaml.dump(dimdict))

    @logged
    def write(self, buf):
        ret = len(buf)

        try:
            old_dims = self.session.query(self.dimension).all()
            dim_data = yaml.load()
            new_dims = []
            for d in dim_data:
                dim = self.dimension(name=d, description=dim_data[d]["description"],
                                     comment=dim_data[d]["comment"])
                new_dims.append(dim)
            for dim in old_dims:
                self.session.delete(dim)
            self.session.flush()
            for dim in new_dims:
                self.session.add(dim)
            self.session.commit()
        except RuntimeError as ex:
            ret = -errno.EIO

        return ret

