#!/usr/bin/env python -3 -t
# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals, print_function


import datetime as dt

import sqlalchemy as sa
import sqlalchemy.orm as orm

from morphdepot.sa.base import Base
from morphdepot.sa.mixins import UUIDMixin, DimensionMixin
from interfaces import Identifiable


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


############
# Dimensions
############
class AnimalSpecies(DimensionMixin, Base):
    __tablename__ = 'animal_species'


class Company(DimensionMixin, Base):
    __tablename__ = 'companies'


class LaborState(DimensionMixin, Base):
    __tablename__ = 'labor_states'


class Colony(DimensionMixin, Base):
    __tablename__ = 'colonies'


##############
# Analog World
##############

class Scientist(Identity):
    __tablename__ = "scientists"
    __mapper_args__ = {'polymorphic_identity': 'Scientist'}
    id = sa.Column(sa.ForeignKey('identities.id'), primary_key=True)
    first_name = sa.Column(sa.String(64), nullable=False)
    middle_name = sa.Column(sa.String(64))
    last_name = sa.Column(sa.String(64), nullable=False)
    title = sa.Column(sa.String(64))
    affiliations = sa.Column(sa.String(128))


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
    animal_id = sa.Column(sa.ForeignKey('animals.id'), unique=True)

    # Properties
    scientist = orm.relationship(
        "Scientist",
        primaryjoin=(scientist_id == Scientist.id),
        backref="experiments")
    animal = orm.relationship(
        "Animal",
        primaryjoin=(animal_id == Animal.id),
        backref="experiments",
        uselist=False)

    # as backrefs:
    # --> tissue_samples


class TissueSample(Identity):
    __tablename__ = 'tissue_samples'
    __mapper_args__ = {'polymorphic_identity': 'TissueSample'}
    id = sa.Column(sa.ForeignKey('identities.id'), primary_key=True)
    label = sa.Column(sa.String(64), unique=True)
    experiment_id = sa.Column(sa.ForeignKey('experiments.id'), nullable=False)

    # Properties
    experiment = orm.relationship(
        "Experiment",
        primaryjoin=(experiment_id == Experiment.id),
        backref="tissue_samples")

    # as backrefs:
    # --> neurons
    # --> digital_neuro_representation


##################
# Conceptual World
##################

class Neuron(Identity):
    __tablename__ = 'neurons'
    __mapper_args__ = {'polymorphic_identity': 'Neuron'}
    id = sa.Column(sa.ForeignKey('identities.id'), primary_key=True)
    tissue_sample_id = sa.Column(sa.ForeignKey('tissue_samples.id'))
    label = sa.Column(sa.String(64), unique=True)

    # Property
    tissue_sample = orm.relationship(
        "TissueSample",
        primaryjoin=(tissue_sample_id == TissueSample.id),
        backref="neurons",
        )


################
# Digital world:
################

# Table to enable n:m-mapping fo Neuron and DigitalNeuroRepresentation
neuron_dnr_maps = sa.Table(
    'neuron_dnr_maps',
    Base.metadata,
    sa.Column('neuron_id', sa.ForeignKey('neurons.id'), primary_key=True),
    sa.Column('dnr_id', sa.ForeignKey('digital_neuro_representations.id'), primary_key=True))


class DigitalNeuroRepresentation(Identity):
    __tablename__ = 'digital_neuro_representations'
    __mapper_args__ = {'polymorphic_identity': 'DigitalNeuroRepresentation'}
    id = sa.Column(sa.ForeignKey('identities.id'), primary_key=True)
    tissue_sample_id = sa.Column(sa.ForeignKey('tissue_samples.id'), nullable=False)
    label = sa.Column(sa.String(64), primary_key=True)
    _checksum = sa.Column(sa.String(32))

    # References
    neurons = orm.relationship(
        "Neuron",
        secondary=neuron_dnr_maps,
        backref='digital_neuro_representations'
    )

    tissue_sample = orm.relationship(
        'TissueSample',
        primaryjoin=(tissue_sample_id == TissueSample.id),
        backref="tissue_samples"
    )

    @property
    def checksum(self):
        return self._checksum
    get_checksum = checksum


class File(Identity):
    __tablename__ = 'files'
    __mapper_args__ = (
        {'polymorphic_identity': 'File'})
    id = sa.Column(sa.ForeignKey('identities.id'), primary_key=True)
    label = sa.Column(sa.String(256), unique=True)
    digital_neuro_representation_id = sa.Column(sa.ForeignKey('digital_neuro_representations.id'))
    _filesize = sa.Column(sa.BigInteger)
    _checksum = sa.Column(sa.String(32))
    __table_args__ = (
        sa.CheckConstraint(_filesize >= 0, name='check_filesize_positive'),
        {})

    # Properties
    digital_neuro_representation = orm.relationship(
        "DigitalNeuroRepresentation",
        primaryjoin=(digital_neuro_representation_id == DigitalNeuroRepresentation.id),
        backref='files')

    @property
    def filesize(self):
        return self._filesize
    get_filesize = filesize

    @property
    def checksum(self):
        return self._checksum
    get_checksum = checksum


if __name__ == '__main__':
    # engine = sa.create_engine('sqlite:///test.sqlite', echo=True)
    engine = sa.create_engine('sqlite://', echo=True)
    engine.execute("PRAGMA foreign_keys=ON") # http://docs.sqlalchemy.org/en/rel_0_7/dialects/sqlite.html#foreign-key-support
    Session = orm.sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    session = Session()


    # Add Scientist
    # #############
    scientist = Scientist(
        first_name="Philipp",
        middle_name="Lothar",
        last_name="Rautenberg",
        affiliations="Ludwig-Maximilians-Universität München, Department Biology II, G-Node, Planegg-Martinsried, Germany")

    session.add(scientist)
    session.commit()


    # Add Dimensions and Animal
    # #########################
    species = []
    companies = []
    labor_states = []
    colonies = []

    dimensions = [species, companies, labor_states, colonies]

    species.append(AnimalSpecies(name='apis mellifera'))
    species.append(AnimalSpecies(name='apis cerena'))

    companies.append(Company(name='Nonogaki'))
    companies.append(Company(name='Akiyta-ya'))
    companies.append(Company(name='Kurume-yoho'))

    labor_states.append(LaborState(name='foreigner'))
    labor_states.append(LaborState(name='nurse'))

    colonies.append(Colony(name='colony_1'))
    colonies.append(Colony(name='colony_2'))

    for dimension in dimensions:
        for data in dimension:
            session.add(data)
    session.commit()

    animal = Animal(
        label="Testtier",
        age=6,
        species="apis mellifera",
        company="Nonogaki",
        colony='colony_1',
        labor_state='nurse')
    session.add(animal)
    session.commit()


    # Add Expermiment
    # ###############
    experiment = Experiment(
        label="my first experiment",
        date=dt.datetime.now(),
        lab_notebook = "here is my labbook entry"
    )
    scientist.experiments.append(experiment)
    session.commit()

    # Add TissueSample
    ##################
    tissue = TissueSample(label="test-tissue")
    tissue.experiment = experiment
    session.commit()


    # Add Neuron
    ############
    neuron = Neuron(label="my favorite neuron!")
    neuron.tissue_sample = tissue
    session.commit()

    # Add DigitalNeuroRepresentation
    ################################
    dnr = DigitalNeuroRepresentation(label='first file associated with a neuron')
    dnr.tissue_sample = tissue
    session.commit()
    # --> the following causes an error using ":memory:"
    # print("%s %s" %(neuron.id, dnr.id))
    # print("******************************************************************************")
    # dnr.neurons.append(neuron)
    # session.commit()
