__author__ = 'philipp'

import datetime as dt
import os
from shutil import copy2

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.associationproxy import association_proxy

from base import Base
from uuid_type import UUIDMixin
from morphdepot import config
from morphdepot.utils.filesystem import get_file_sha1

"""
The Model also reads and writes to the file system!
"""

###############
# RESTful World
###############

resource_tag_maps = sa.Table(
    'resource_tag_maps',
    Base.metadata,
    sa.Column('resource_uuid', sa.ForeignKey('resources.uuid'), primary_key=True),
    sa.Column('tag_uuid', sa.ForeignKey('tags.uuid'), primary_key=True))

def find_or_create_tag(kw):
    tag = Tag.query.filter_by(name=kw).first()
    if not(tag):
        tag = Tag(name=kw)
        # if aufoflush=False used in the session, then uncomment below
        if not hasattr(Tag, "session"):
            Tag.session = DBSession()
        Tag.session.add(tag)
        Tag.session.flush()
    return tag


class Tag(UUIDMixin, Base):
    __tablename__ = 'tags'
    name = sa.Column(sa.String, unique=True, nullable=False)

    def __init__(self, name):
        self.name = name


class Resource(UUIDMixin, Base):
    __tablename__ = 'resources'
    mtime = sa.Column(
        'mtime',
        sa.DateTime,
        default=dt.datetime.now())
    ctime = sa.Column(
        'ctime',
        sa.DateTime,
        default=dt.datetime.now())
    _dto_type = sa.Column('dto_type', sa.String, nullable=False)
    __mapper_args__ = {'polymorphic_on': _dto_type}


    # tags & proxy the 'keyword' attribute from the 'kw' relationship
    tag_objects = orm.relationship('Tag',
                                   secondary=resource_tag_maps,
                                   backref='tagged')
    tags = association_proxy('tag_objects', 'name',
                             creator=find_or_create_tag)


##############
# Analog World
##############

class Scientist(Resource):
    __tablename__ = "scientists"
    __mapper_args__ = {'polymorphic_identity': 'Scientist'}
    uuid = sa.Column(sa.ForeignKey('resources.uuid'), primary_key=True)
    first_name = sa.Column(sa.String(64), nullable=False)
    middle_name = sa.Column(sa.String(64))
    last_name = sa.Column(sa.String(64), nullable=False)
    title = sa.Column(sa.String(64))
    affiliations = sa.Column(sa.String(128))

    @staticmethod
    def caption2name(caption):
        """
        Format rule: LASTNAME__FIRSTNAME

        Examples
        ========

        caption2name("Mayer_Huber__Max")
        --> {"last_name":  "Mayer Huber",
             "first_name": "Max"}
        """
        try:
            ln, fn = caption.split("__")
            last_name = ln.replace("_", " ")
            first_name = fn.replace("_", " ")
        except e:
            print e
        return {'last_name': last_name, 'first_name': first_name}

    @property
    def caption(self):
        caption = "%s %s" %(self.last_name, self.first_name)
        return caption.replace(" ", "__")

    @caption.setter
    def caption(self, value):

        try:
            ln, fn = value.split("__")
            self.last_name = ln.replace("_", " ")
            self.first_name = ln.replace("_", " ")
        except e:
            print e


# Helper Class for Animal
class AnimalSpecies(Base):
    __tablename__ = 'animal_species'
    label = sa.Column(sa.String(64), primary_key=True)


class Animal(Resource):
    __tablename__ = 'animals'
    __mapper_args__ = {'polymorphic_identity': 'Animal'}
    uuid = sa.Column(sa.ForeignKey('resources.uuid'), primary_key=True)
    label = sa.Column(sa.String(64), unique=True)
    species = sa.Column(sa.ForeignKey('animal_species.label'))
    age = sa.Column(sa.Integer)
    age_uncertainty = sa.Column(sa.String(64))



class Experiment(Resource):
    __tablename__ = "experiments"
    __mapper_args__ = {'polymorphic_identity': 'Experiment'}
    uuid = sa.Column(sa.ForeignKey('resources.uuid'), primary_key=True)
    label = sa.Column(sa.String(64), nullable=False, unique=True)
    date = sa.Column(sa.DateTime, nullable=False)
    lab_book_entry = sa.Column(sa.Text)
    scientist_uuid = sa.Column(sa.ForeignKey('scientists.uuid'))
    animal_uuid = sa.Column(sa.ForeignKey('animals.uuid'), unique=True)

    # Properties
    scientist = orm.relationship(
        "Scientist",
        primaryjoin=(scientist_uuid == Scientist.uuid),
        backref="experiments")
    animal = orm.relationship(
        "Animal",
        primaryjoin=(animal_uuid == Animal.uuid),
        backref="experiments",
        uselist=False)

    # as backrefs:
    # --> tissue_samples


class TissueSample(Resource):
    __tablename__ = 'tissue_samples'
    __mapper_args__ = {'polymorphic_identity': 'TissueSample'}
    uuid = sa.Column(sa.ForeignKey('resources.uuid'), primary_key=True)
    label = sa.Column(sa.String(64), unique=True)
    experiment_uuid = sa.Column(sa.ForeignKey('experiments.uuid'))

    # Properties
    experiment = orm.relationship(
        "Experiment",
        primaryjoin=(experiment_uuid == Experiment.uuid),
        backref="tissue_samples")

    # as backrefs:
    # --> neurons
    # --> digital_neuro_representation


##################
# Conceptual World
##################

class Neuron(Resource):
    __tablename__ = 'neurons'
    __mapper_args__ = {'polymorphic_identity': 'Neuron'}
    uuid = sa.Column(sa.ForeignKey('resources.uuid'), primary_key=True)
    tissue_sample_uuid = sa.Column(sa.ForeignKey('tissue_samples.uuid'))
    label = sa.Column(sa.String(64), unique=True)

    # Property
    tissue_sample = orm.relationship(
        "TissueSample",
        primaryjoin=(tissue_sample_uuid == TissueSample.uuid),
        backref="neurons",
        )


################
# Digital world:
################
class FileSet(Resource):
    __tablename__ = 'file_sets'
    __mapper_args__ = (
        {'polymorphic_identity': 'FileSet'})
    uuid = sa.Column(sa.ForeignKey('resources.uuid'), primary_key=True)
    label = sa.Column(sa.String(256), unique=True)
    _checksum = sa.Column(sa.String(32))

    @property
    def root_path(self):
        root_path = config['RAW_DATA_ROOT']
        assert os.path.isdir(root_path), '%s does not exist!' %(root_path)
        return root_path

    @property
    def abs_path(self):
        import os
        return os.path.join(self.root_path, unicode(self.uuid))


class File(Resource):
    __tablename__ = 'files'
    __mapper_args__ = (
        {'polymorphic_identity': 'File'})
    uuid = sa.Column(sa.ForeignKey('resources.uuid'), primary_key=True)
    filename = sa.Column(sa.String(256))
    file_set_uuid = sa.Column(sa.ForeignKey('file_sets.uuid'), nullable=False)
    path_origin = sa.Column(sa.Unicode)
    _filesize = sa.Column(sa.BigInteger)
    _checksum = sa.Column(sa.String(32))
    __table_args__ = (
        sa.CheckConstraint(_filesize >= 0, name='check_filesize_positive'),
        sa.UniqueConstraint(filename, file_set_uuid),
        {})


    # Properties
    file_set = orm.relationship(
        "FileSet",
        primaryjoin=(file_set_uuid == FileSet.uuid),
        backref='files')

    @property
    def abs_path(self):
        return os.path.join(self.file_set.abs_path, self.filename)


    @property
    def filesize(self):
        return self._filesize

    # as backref:
    # --> digital_neuron_representation


# Helper-Plugin-Class for individual Digital-Reprensentation-Definitions
neuron_dnr_maps = sa.Table(
    'neuron_dnr_maps',
    Base.metadata,
    sa.Column('neuron_uuid', sa.ForeignKey('neurons.uuid'), primary_key=True),
    sa.Column('dnr_uuid', sa.ForeignKey('digital_neuron_representations.uuid'), primary_key=True))


class DigitalNeuronRepresentation(Resource):
    __tablename__ = 'digital_neuron_representations'
    __mapper_args__ = {'polymorphic_identity': 'DigitalNeuronRepresentation'}
    uuid = sa.Column(sa.ForeignKey('resources.uuid'), primary_key=True)
    file_set_uuid = sa.Column(sa.ForeignKey('file_sets.uuid'), unique=True)
    label = sa.Column(sa.String(64), primary_key=True)

    file_set = orm.relationship(
        'FileSet',
        primaryjoin=(file_set_uuid == FileSet.uuid),
        backref = 'digital_neuron_representations',
        uselist=False,
    )

    # References
    neurons = orm.relationship(
        "Neuron",
        secondary=neuron_dnr_maps,
        backref='digital_neuron_representations'
    )


class MicroscopeImageStack(DigitalNeuronRepresentation):
    __tablename__ = 'microscope_image_stacks'
    __mapper_args__ = {'polymorphic_identity': 'MicroscopeImageStack'}
    uuid = sa.Column(sa.ForeignKey('digital_neuron_representations.uuid'), primary_key=True)


class Segmentation(DigitalNeuronRepresentation):
    __tablename__ = 'segmentations'
    __mapper_args__ = {'polymorphic_identity': 'Segmentation'}
    uuid = sa.Column(sa.ForeignKey('digital_neuron_representations.uuid'), primary_key=True)
    microscope_image_stack_uuid = sa.Column(sa.ForeignKey(
        'microscope_image_stacks.uuid'),
                                            nullable=False)

    # References
    microscope_image_stack = orm.relationship(
        'MicroscopeImageStack',
        primaryjoin=(microscope_image_stack_uuid == MicroscopeImageStack.uuid),
        backref='segmentation',
    )


class MicroscopeImage(DigitalNeuronRepresentation):
    __tablename__ = 'microscope_images'
    __mapper_args__ = {'polymorphic_identity': 'MicroscopeImage'}
    uuid = sa.Column(sa.ForeignKey('digital_neuron_representations.uuid'), primary_key=True)


class ElectroPhysiology(DigitalNeuronRepresentation):
    __tablename__ = 'electro_physiologies'
    __mapper_args__ = {'polymorphic_identity': 'ElectroPhysiology'}
    uuid = sa.Column(sa.ForeignKey('digital_neuron_representations.uuid'), primary_key=True)


##################
# AddOn: Equipment
##################

equipment_experiment_maps = sa.Table(
    'equipment_experiment_maps',
    Base.metadata,
    sa.Column('equipment_uuid', sa.ForeignKey('equipments.uuid'), primary_key=True),
    sa.Column('experiment_uuid', sa.ForeignKey('experiments.uuid'), primary_key=True))

equipment_dnr_maps = sa.Table(
    'equipment_dnr_maps',
    Base.metadata,
    sa.Column('equipment_uuid', sa.ForeignKey('equipments.uuid'), primary_key=True),
    sa.Column('dnr_uuid', sa.ForeignKey('digital_neuron_representations.uuid'), primary_key=True))


class Equipment(Resource):
    __tablename__ = "equipments"
    __mapper_args__ = {'polymorphic_identity': 'Equipment'}
    uuid = sa.Column(sa.ForeignKey('resources.uuid'), primary_key=True)
    label = sa.Column(sa.String(64), unique=True)

    experiments = orm.relationship('Experiment',
                                   secondary=equipment_experiment_maps,
                                   backref='equipments')

    digital_neuron_representations = orm.relationship('DigitalNeuronRepresentation',
                                   secondary=equipment_dnr_maps,
                                   backref='equipments')


class Sigen(Equipment):
    """
    Todo: move to ext.equipments
    """
    __tablename__ = "sigens"
    __mapper_args__ = {'polymorphic_identity': 'Sigen'}
    uuid = sa.Column(sa.ForeignKey('equipments.uuid'), primary_key=True)
    version = sa.Column(sa.String(64), nullable=False)
    d_parameter = sa.Column(sa.Integer, nullable=False)
    v_parameter = sa.Column(sa.Integer, nullable=False)
    c_parameter = sa.Column(sa.Integer, nullable=False)
    s_parameter = sa.Column(sa.Integer, nullable=False)


########
# Events
########

def set_file_attributes(mapper, connection, target):
    file_abs_path = target.path_origin
    print "file_abs_path: %s, file_set.abs_path: %s" %(file_abs_path, target.file_set.abs_path)
    target.filename = os.path.basename(file_abs_path)
    target._filesize = os.path.getsize(file_abs_path)
    target._checksum = get_file_sha1(file_abs_path)
    copy2(target.path_origin, target.file_set.abs_path)

def adjust_checksum_file_set(mapper, connection, target):
    """
    hash = hashlib.sha1()
    for file in self.uploadedfile_set.all():
        hash.update(file.checksum)
    self.checksum = hash.hexdigest()
    self.path = os.path.join(utils.ROOT_FILEFOLDERS, self.uuid)
    super(FileFolder, self).save(*args, **kwargs)
    """
    pass

def create_file_set_folder(mapper, connection, target):
    os.mkdir(target.abs_path)

# def copy_file_to_fileset_location(mapper, connection, target):

sa.event.listen(File, 'before_insert', set_file_attributes)
sa.event.listen(FileSet, 'after_insert', create_file_set_folder)
# sa.event.listen(File, 'after_insert')