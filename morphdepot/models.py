#!/usr/bin/env python -3 -t
# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals, print_function


import datetime as dt

import sqlalchemy as sa
import sqlalchemy.orm as orm

from morphdepot.sa.base import Base
from morphdepot.sa.mixins import UUIDMixin, IDMixin, DimensionMixin
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

# Animal specific
class AnimalSpecies(DimensionMixin, Base):
    __tablename__ = 'animal_species'


class Company(DimensionMixin, Base):
    __tablename__ = 'companies'


class LaborState(DimensionMixin, Base):
    __tablename__ = 'labor_states'


class Colony(DimensionMixin, Base):
    __tablename__ = 'colonies'

# Neuron specific
class NeuronCategory(DimensionMixin, Base):
    __tablename__ = 'neuron_categories'

class Arborization_Area(DimensionMixin, Base):
    __tablename__ = 'arborization_areas'

class CellBodyRegion(DimensionMixin, Base):
    __tablename__ = 'cell_body_regions'

class Axonal_Tract(DimensionMixin, Base):
    __tablename__ = 'axonal_tracts'


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
    # --> neuro_representation


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
    _checksum = sa.Column(sa.String(32))

    # References
    neurons = orm.relationship(
        "Neuron",
        secondary=neuron_nr_maps,
        backref='neuro_representations'
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
    neuro_representation_id = sa.Column(sa.ForeignKey('neuro_representations.id'))
    _filesize = sa.Column(sa.BigInteger)
    _checksum = sa.Column(sa.String(32))
    __table_args__ = (
        sa.CheckConstraint(_filesize >= 0, name='check_filesize_positive'),
        {})

    # Properties
    neuro_representation = orm.relationship(
        "NeuroRepresentation",
        primaryjoin=(neuro_representation_id == NeuroRepresentation.id),
        backref='files')

    @property
    def filesize(self):
        return self._filesize
    get_filesize = filesize

    @property
    def checksum(self):
        return self._checksum
    get_checksum = checksum

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
    id = sa.Column(sa.BigInteger, primary_key=True)
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

if __name__ == '__main__':

    db_server = "postgresql"
    pg_schema = "ginjang_ndb"
    pg_recreate_schema = True
    add_test_data = True

    if db_server == "sqlite":
        # engine = sa.create_engine('sqlite:///test.sqlite', echo=True)
        engine = sa.create_engine('sqlite://', echo=True)
        engine.execute("PRAGMA foreign_keys=ON") # http://docs.sqlalchemy.org/en/rel_0_7/dialects/sqlite.html#foreign-key-support
    elif db_server == "postgresql":
        engine = sa.create_engine('postgresql://dev_rautenbe@ama-prod/develop', echo=True)
        results = engine.execute("SHOW search_path;")
        for result in results:
            assert result[0] == pg_schema, "search_path not set correctly"
        results.close()
        if pg_recreate_schema: # recreate schema
            engine.execute("DROP SCHEMA %s CASCADE;" %(pg_schema))
            engine.execute("CREATE SCHEMA %s;" %(pg_schema))

    Session = orm.sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    session = Session()

    if add_test_data: # Add test data
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

        # Add NeuroRepresentation
        ################################
        nr = NeuroRepresentation(label='first file associated with a neuron')
        nr.tissue_sample = tissue
        session.commit()
        # --> the following causes an error using ":memory:"
        # print("%s %s" %(neuron.id, nr.id))
        # print("******************************************************************************")
        # nr.neurons.append(neuron)
        # session.commit()

        # Permission
        animal.permission = Permisson()
        print(animal.permission.oga)
