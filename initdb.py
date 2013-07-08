#!/usr/bin/env python

from __future__ import division, unicode_literals, print_function

import datetime
import sqlalchemy
import sqlalchemy.orm

from morphdepot.log import logged

import morphdepot.config as config
import morphdepot.models as models
import morphdepot.models.core as core
import morphdepot.models.morph as morph
import morphdepot.models.ephys as ephys
import morphdepot.models.dimensions as dimensions

from morphdepot.models import Base
from morphdepot.models.core import Scientist, Animal, Experiment, \
    TissueSample, Protocol, Neuron, NeuroRepresentation, File, \
    PreparatioCondition, Permisson
from morphdepot.models.morph import MicroscopeImage, MicroscopeImageStack, \
    Segmentation, HSBRegistration
from morphdepot.models.ephys import Electrophysiology
from morphdepot.models.dimensions import AnimalSpecies, Company, LaborState, \
    Colony, NeuronCategory, ArborizationArea, CellBodyRegion, AxonalTract, \
    Software, GeneralParam, ResponseProperty, SpontaneousActivity


engine = None
session = None
connected = False


@logged
def db_connect():
    global engine
    global session
    global connected
    if not connected:
        engine = sqlalchemy.create_engine(config.DB['url'], echo=config.DB['echo'])
        if config.DB['type'] == "sqlite":
            engine.execute("PRAGMA foreign_keys=ON")
        elif config.DB['type'] == "postgresql" and config.DB['pg_recreate_schema']:
                engine.execute("DROP SCHEMA %s CASCADE;" % (config.DB['schema']))
                engine.execute("CREATE SCHEMA %s;" % (config.DB['schema']))
        Session = sqlalchemy.orm.sessionmaker(bind=engine)
        Base.metadata.create_all(engine)
        session = Session()
        connected = True


@logged
def db_create():
    if connected:
        Base.metadata.create_all(engine)


@logged
def db_populate():
    if connected:
        # Add Scientist
        # #############
        scientist = Scientist(
            first_name="Philipp",
            middle_name="Lothar",
            last_name="Rautenberg",
            author_notation="Philipp L. Rautenberg",
            affiliations="Ludwig-Maximilians-Universitaet Muenchen"
        )

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
            date=datetime.datetime.now(),
            lab_notebook="here is my labbook entry"
        )
        scientist.experiments.append(experiment)
        session.commit()

        # Add TissueSample
        ##################
        tissue = TissueSample(label="test-tissue")
        tissue.animal = animal
        tissue.experiment = experiment
        session.commit()

        # Add Protocol
        ##############
        protocol = Protocol(label="protocol 1", description="did something")
        tissue.protocols.append(protocol)

        # Add Neuron
        ############
        neuron = Neuron(label="my favorite neuron!")

        # Add NeuroRepresentation
        ################################
        nr = NeuroRepresentation(label='first file associated with a neuron')
        tissue.neuro_representations.append(nr)
        # nr.tissue_sample = tissue
        session.commit()
        nr.neurons.append(neuron)
        session.commit()

        # File
        ######
        file_object = nr.add_file("initdb.py")
        print(file_object.st_size)
        session.commit()

        # Permission
        animal.permission = Permisson()
        print(animal.permission.oga)
        session.commit()

        #########
        # morph #
        #########
        mi = MicroscopeImage(label="my first microscope image")
        mis = MicroscopeImageStack(label="my first microscope image stack")

        tissue.neuro_representations.append(mi)
        tissue.neuro_representations.append(mis)
        session.commit()

        seg = Segmentation(label="my first segmentation")
        seg.scientist = scientist
        seg.microscope_image_stack = mis
        seg.tissue_sample = tissue
        session.commit()

        # working with dimensions
        session.add(Software(name="SIGEN"))
        session.commit()
        param = GeneralParam(name='Param1')
        seg.software = "SIGEN"
        seg.general_params.append(param)
        session.commit()

        #########
        # ephys #
        #########
        session.add(SpontaneousActivity(name="first spontaneous activity"))
        response_property = ResponseProperty(name="first response Property")
        session.add(response_property)
        session.commit()

        ephys = Electrophysiology(
            label="my first electrophysiology",
            spontaneous_activity='first spontaneous activity',
            quality_rank=1,
            stim_vibration_frequency=1.5,
            tissue_sample=tissue,
            response_properties=[response_property]
        )
        # tissue.neuro_representations.append(ephys)
        session.commit()

# Do things ...
if __name__ == "__main__":
    # ... on execution
    db_connect()
    db_create()
    if config.DB['add_test_data']:
        db_populate()
else:
    # ... on import *
    db_connect()
