#!/usr/bin/env python -3 -t
# -*- coding: utf-8 -*-

import datetime as dt
import os
import hashlib
import shutil

import sqlalchemy as sa
import sqlalchemy.orm as orm

import uuid as uuid_package

from morphdepot.models import Base
from morphdepot.models.utils.mixins import UUIDMixin, IDMixin
from morphdepot.models.interfaces import Identifiable
from morphdepot.models.dimensions import *

import morphdepot.config as config


class Identity(UUIDMixin, Base, Identifiable):
    __tablename__ = 'identities'
    mtime = sa.Column(
        'mtime',
        sa.DateTime,
        default=dt.datetime.now)
    ctime = sa.Column(
        'ctime',
        sa.DateTime,
        default=dt.datetime.now)
    _dto_type = sa.Column('dto_type', sa.String, nullable=False)
    __mapper_args__ = {'polymorphic_on': _dto_type}

    @staticmethod
    def update_mtime(mapper, connection, target):
        target.mtime = dt.datetime.now()

    @classmethod
    def __declare_last__(cls):
        sa.event.listen(cls, 'before_update', cls.update_mtime)


##############
# Analog World
##############

class Scientist(IDMixin, Identity):
    __tablename__ = "scientists"
    __mapper_args__ = {'polymorphic_identity': 'Scientist'}
    # id = sa.Column(sa.ForeignKey('identities.id'), primary_key=True)
    first_name = sa.Column(sa.String(64), nullable=False)
    middle_name = sa.Column(sa.String(64))
    last_name = sa.Column(sa.String(64), nullable=False)
    title = sa.Column(sa.String(64))
    affiliations = sa.Column(sa.String(128))

    def __str__(self):
        return "%s %s %s, mtime: %s, ctime: %s" %(
            self.first_name,
            self.middle_name,
            self.last_name,
            self.mtime,
            self.ctime,
        )


class Animal(Identity):
    __tablename__ = 'animals'
    __mapper_args__ = {'polymorphic_identity': 'Animal'}
    id = sa.Column(sa.ForeignKey('identities.id'), primary_key=True)
    label = sa.Column(sa.String(64), unique=True)
    age = sa.Column(sa.Integer)
    species = sa.Column(sa.ForeignKey('animal_species.name'), nullable=False)
    company = sa.Column(sa.ForeignKey('companies.name'), nullable=False)
    labor_state = sa.Column(sa.ForeignKey("labor_states.name"), nullable=False)
    colony = sa.Column(sa.ForeignKey('colonies.name'), nullable=False)


class Experiment(Identity):
    __tablename__ = "experiments"
    __mapper_args__ = {'polymorphic_identity': 'Experiment'}
    id = sa.Column(sa.ForeignKey('identities.id'), primary_key=True)
    label = sa.Column(sa.String(64), nullable=False, unique=True)
    date = sa.Column(sa.DateTime, nullable=False)
    lab_notebook = sa.Column(sa.Text)
    scientist_id = sa.Column(sa.ForeignKey('scientists.id'), nullable=False)

    # Properties
    scientist = orm.relationship(
        "Scientist",
        primaryjoin=(scientist_id == Scientist.id),
        backref="experiments")


class TissueSample(Identity):
    __tablename__ = 'tissue_samples'
    __mapper_args__ = {'polymorphic_identity': 'TissueSample'}
    id = sa.Column(sa.ForeignKey('identities.id'), primary_key=True)
    label = sa.Column(sa.String(64), unique=True)
    experiment_id = sa.Column(sa.ForeignKey('experiments.id'), nullable=False)
    animal_id = sa.Column(sa.ForeignKey('animals.id'), unique=True)

    # Properties
    experiment = orm.relationship(
        "Experiment",
        primaryjoin=(experiment_id == Experiment.id),
        backref="tissue_samples")
    animal = orm.relationship(
        "Animal",
        primaryjoin=(animal_id == Animal.id),
        backref="tissue_samples",
        uselist=False)


##################
# Conceptual World
##################

class Neuron(Identity):
    __tablename__ = 'neurons'
    __mapper_args__ = {'polymorphic_identity': 'Neuron'}
    id = sa.Column(sa.ForeignKey('identities.id'), primary_key=True)
    label = sa.Column(sa.String(64), unique=True)
    comment = sa.Column(sa.Text)
    # Dimensions:
    neuron_category = sa.Column(sa.ForeignKey(NeuronCategory.name))
    arborization_area = sa.Column(sa.ForeignKey(Arborization_Area.name))
    cell_body_region = sa.Column(sa.ForeignKey(CellBodyRegion.name))
    axonal_tract = sa.Column(sa.ForeignKey(Axonal_Tract.name))


################
# Digital world:
################

# Table to enable n:m-mapping fo Neuron and NeuroRepresentation
neuron_nr_maps = sa.Table(
    'neuron_nr_maps',
    Base.metadata,
    sa.Column('neuron_id', sa.ForeignKey('neurons.id'), primary_key=True),
    sa.Column('nr_id', sa.ForeignKey('neuro_representations.id'), primary_key=True))


class NeuroRepresentation(Identity):
    __tablename__ = 'neuro_representations'
    __mapper_args__ = {'polymorphic_identity': 'NeuroRepresentation'}
    id = sa.Column(sa.ForeignKey('identities.id'), primary_key=True)
    tissue_sample_id = sa.Column(sa.ForeignKey('tissue_samples.id'), nullable=False)
    label = sa.Column(sa.String(64), unique=True)
    _checksum = sa.Column(sa.String(40))

    def __init__(self, label):
        self.label = label
        self.update_checksum()
        self.id = uuid_package.uuid4()
        os.makedirs(self.get_abs_path())

    # References
    neurons = orm.relationship(
        "Neuron",
        secondary=neuron_nr_maps,
        backref='neuro_representations'
    )

    tissue_sample = orm.relationship(
        'TissueSample',
        primaryjoin=(tissue_sample_id == TissueSample.id),
        backref="neuron_representations"
    )

    @property
    def checksum(self):
        return self._checksum
    get_checksum = checksum

    def update_checksum(self):
        print("updating checksum")
        hash = hashlib.sha1()
        for file in self.files:
            hash.update(file.checksum)
        self._checksum = hash.hexdigest()
        print(self._checksum)

    def get_abs_path(self):
        return os.path.join(config.RAW_DATA['root_dir'], str(self.id))

    def add_file(self, path_to_file):
        file_name = os.path.basename(path_to_file)
        stat = os.stat(path_to_file)
        file_object = File(
            file_name = file_name,
            st_atime = dt.datetime.fromtimestamp(stat.st_atime),
            st_mtime = dt.datetime.fromtimestamp(stat.st_mtime),
            st_ctime = dt.datetime.fromtimestamp(stat.st_ctime),
            st_blksize = stat.st_blksize,
            st_size = stat.st_size,
        )

        self.files.append(file_object)
        shutil.copy2(path_to_file, os.path.join(self.get_abs_path(), file_name))
        file_object.update_checksum()
        return file_object

    @staticmethod
    def auto_delete_directory(mapper, connection, target):
        print(target.get_abs_path())
        os.rmdir(target.get_abs_path())

sa.event.listen(NeuroRepresentation, 'before_delete', NeuroRepresentation.auto_delete_directory)


class File(Identity):
    __tablename__ = 'files'
    __mapper_args__ = (
        {'polymorphic_identity': 'File'})
    id = sa.Column(sa.ForeignKey('identities.id'), primary_key=True)
    file_name = sa.Column(sa.String(256)) # unique with neuron_representation.id ?
    neuro_representation_id = sa.Column(sa.ForeignKey('neuro_representations.id'), nullable=False)
    st_atime = sa.Column(sa.DateTime)
    st_mtime = sa.Column(sa.DateTime)
    st_ctime = sa.Column(sa.DateTime)
    st_blksize = sa.Column(sa.Integer)
    st_size = sa.Column(sa.BigInteger)
    _checksum = sa.Column(sa.String(40))
    __table_args__ = (
        sa.CheckConstraint(st_size >= 0, name='check_filesize_positive'),
        {})

    # Properties
    neuro_representation = orm.relationship(
        "NeuroRepresentation",
        primaryjoin=(neuro_representation_id == NeuroRepresentation.id),
        backref=orm.backref('files', cascade="all,delete"))

    @property
    def checksum(self):
        return self._checksum
    get_checksum = checksum

    def get_abs_path(self):
        return os.path.join(self.neuro_representation.get_abs_path(), self.file_name)

    def update_checksum(self):
        f = open(self.get_abs_path())
        hash = hashlib.sha1()
        hash.update(f.read())
        f.close()
        self._checksum = hash.hexdigest()
        self.neuro_representation.update_checksum()

    # Triggers
    @staticmethod
    def delete_file(mapper, connection, target):
        os.remove(target.get_abs_path())

sa.event.listen(File, 'after_delete', File.delete_file)


# GinJang: Method-Information
#############################

class PreparatioCondition(Identity):
    __tablename__ = "preparation_condition"
    __mapper_args__ = {'polymorphic_identity': 'PreparationCondition'}
    id = sa.Column(sa.ForeignKey('identities.id'), primary_key=True)
    experiment_id = sa.Column(sa.ForeignKey('experiments.id'), nullable=False)
    duration_incubation = sa.Column(sa.Integer, nullable=False)
    preparation_date = sa.Column(sa.DateTime, nullable=False)

    # relationships
    experiment = orm.relationship(
        "Experiment",
        primaryjoin=(experiment_id == Experiment.id),
        backref='preparation_condition'
    )


# Add On: Permission
####################

class Permisson(Base):
    __tablename__ = "permissions"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    identity_id = sa.Column(sa.ForeignKey('identities.id'), unique=True)
    oga = sa.Column(sa.String(9), nullable=False, default="rw-------")
    user = sa.Column(sa.Integer, nullable=False)
    group = sa.Column(sa.Integer, nullable=False)

    def __init__(self, oga="rw-------", user=1, group=1):
        self.oga = oga
        self.user = user
        self.group = group

    # relationships
    identity = orm.relationship(
        "Identity",
        backref=orm.backref('permission', uselist=False)
    )

# from sqlalchemy.ext.associationproxy import association_proxy
#
# Identity.oga = association_proxy('permission', 'oga')
