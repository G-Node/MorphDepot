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

        scientist = Scientist(
            first_name="Andrey",
            last_name="Sobolev",
            author_notation="A. Sobolev",
            affiliations="Ludwig-Maximilians-Universitaet Muenchen"
        )
        session.add(scientist)

        scientist = Scientist(
            first_name="Adrian",
            last_name="Stoewer",
            author_notation="Adrian D. Stoewer",
            affiliations="Ludwig-Maximilians-Universitaet Muenchen"
        )
        session.add(scientist)
        session.commit()

        all_scientists = session.query(Scientist).order_by(Scientist.author_notation).all()

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

        animal = Animal(label="Testtier", age=6, species="apis mellifera", company="Nonogaki",
                        colony='colony_1', labor_state='nurse')
        session.add(animal)
        session.commit()

        # Add Expermiment
        # ###############
        experiment = Experiment(
            label="Exp 01",
            date=datetime.datetime.now(),
            lab_notebook="here is my labbook entry"
        )
        all_scientists[2].experiments.append(experiment)

        experiment = Experiment(
            label="Exp 02",
            date=datetime.datetime.now(),
            lab_notebook="here is my labbook entry"
        )
        all_scientists[2].experiments.append(experiment)

        experiment = Experiment(
            label="Exp 03",
            date=datetime.datetime.now(),
            lab_notebook="here is my labbook entry"
        )
        all_scientists[1].experiments.append(experiment)

        experiment = Experiment(
            label="Exp 04",
            date=datetime.datetime.now(),
            lab_notebook="here is my labbook entry"
        )
        all_scientists[0].experiments.append(experiment)
        session.commit()

        all_experiments = session.query(Experiment).order_by(Experiment.label).all()

        # Add Protocol
        ##############
        session.add(Protocol(label="Protocol 01", description="did something"))
        session.add(Protocol(label="Protocol 02", description="did something really cool"))
        session.add(Protocol(label="Protocol 03", description="apply liquid a to unknown thing"))
        session.add(Protocol(label="Protocol 04", description="this protocol can't work at all"))
        session.add(Protocol(label="Protocol 05", description="did something else"))
        session.add(Protocol(label="Protocol 06", description="apply background dye"))
        session.commit()

        all_protocols = session.query(Protocol).order_by(Protocol.label).all()

        # Add TissueSample
        ##################
        tissue = TissueSample(label="Tissue 01")
        tissue.animal = Animal(label="Bee 01", age=6, species="apis mellifera", company="Nonogaki",
                               colony="colony_1", labor_state="foreigner")
        tissue.experiment = all_experiments[0]
        tissue.protocols.append(all_protocols[0])
        tissue.protocols.append(all_protocols[2])

        tissue = TissueSample(label="Tissue 02")
        tissue.animal = Animal(label="Bee 02", age=6, species="apis mellifera", company="Akiyta-ya",
                               colony="colony_2", labor_state="nurse")
        tissue.experiment = all_experiments[0]
        tissue.protocols.append(all_protocols[4])
        tissue.protocols.append(all_protocols[5])

        tissue = TissueSample(label="Tissue 03")
        tissue.animal = Animal(label="Bee 04", age=6, species="apis cerena", company="Nonogaki",
                               colony="colony_1", labor_state="nurse")
        tissue.experiment = all_experiments[1]
        tissue.protocols.append(all_protocols[3])

        tissue = TissueSample(label="Tissue 04")
        tissue.animal = Animal(label="Bee 06", age=6, species="apis mellifera", company="Akiyta-ya",
                               colony="colony_2", labor_state="foreigner")
        tissue.experiment = all_experiments[1]
        tissue.protocols.append(all_protocols[0])
        tissue.protocols.append(all_protocols[1])
        tissue.protocols.append(all_protocols[4])
        session.commit()

        all_tissues = session.query(TissueSample).order_by(TissueSample.label).all()

        # Add Neuron
        ############
        session.add(Neuron(label="Neuron 01"))
        session.add(Neuron(label="Neuron 02"))
        session.add(Neuron(label="Neuron 03"))
        session.add(Neuron(label="Neuron 04"))
        session.commit()

        all_neurons = session.query(Neuron).order_by(Neuron.label).all()

        # Add NeuroRepresentation
        ################################
        #nr = NeuroRepresentation(label='first file associated with a neuron')
        #nr.tissue_sample = all_tissues[0]
        #nr.neurons.append(all_neurons[0])

        #session.commit()

        # File
        ######
        #file_object = nr.add_file("initdb.py")
        #print(file_object.st_size)
        #session.commit()

        # Permission
        animal.permission = Permisson()
        print(animal.permission.oga)
        session.commit()

        #########
        # morph #
        #########
        mi = MicroscopeImage(label="Image 01")
        mi.add_file("initdb.py")
        mi.neurons.append(all_neurons[0])
        mi.tissue_sample = all_tissues[0]

        mi = MicroscopeImage(label="Image 02")
        mi.add_file("initdb.py")
        mi.neurons.append(all_neurons[0])
        mi.tissue_sample = all_tissues[0]

        mi = MicroscopeImage(label="Image 03")
        mi.add_file("initdb.py")
        mi.neurons.append(all_neurons[1])
        mi.tissue_sample = all_tissues[1]

        mi = MicroscopeImage(label="Image 04")
        mi.add_file("initdb.py")
        mi.tissue_sample = all_tissues[1]

        mi = MicroscopeImage(label="Image 05")
        mi.add_file("initdb.py")
        mi.neurons.append(all_neurons[2])
        mi.tissue_sample = all_tissues[2]
        session.commit()

        all_images = session.query(MicroscopeImage).order_by(MicroscopeImage.label).all()

        mis = MicroscopeImageStack(label="Image stack 01")
        mis.add_file("initdb.py")
        mis.neurons.append(all_neurons[0])
        mis.tissue_sample = all_tissues[0]

        mis = MicroscopeImageStack(label="Image stack 02")
        mis.add_file("initdb.py")
        mis.neurons.append(all_neurons[0])
        mis.tissue_sample = all_tissues[1]

        mis = MicroscopeImageStack(label="Image stack 03")
        mis.add_file("initdb.py")
        mis.tissue_sample = all_tissues[1]

        mis = MicroscopeImageStack(label="Image stack 04")
        mis.add_file("initdb.py")
        mis.tissue_sample = all_tissues[2]

        mis = MicroscopeImageStack(label="Image stack 05")
        mis.add_file("initdb.py")
        mis.tissue_sample = all_tissues[2]
        session.commit()

        all_image_stacks = session.query(MicroscopeImageStack).order_by(MicroscopeImageStack.label).all()

        #seg = Segmentation(label="my first segmentation")
        #seg.scientist = scientist
        #seg.microscope_image_stack = mis
        #seg.tissue_sample = tissue
        #session.commit()

        # working with dimensions
        #session.add(Software(name="SIGEN"))
        #session.commit()
        #param = GeneralParam(name='Param1')
        #seg.software = "SIGEN"
        #seg.general_params.append(param)
        #session.commit()

        #########
        # ephys #
        #########
        #session.add(SpontaneousActivity(name="first spontaneous activity"))
        #response_property = ResponseProperty(name="first response Property")
        #session.add(response_property)
        #session.commit()

        #ephys = Electrophysiology(
        #    label="my first electrophysiology",
        #    spontaneous_activity='first spontaneous activity',
        #    quality_rank=1,
        #    stim_vibration_frequency=1.5,
        #    tissue_sample=tissue,
        #    response_properties=[response_property]
        #)
        # tissue.neuro_representations.append(ephys)
        #session.commit()

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
