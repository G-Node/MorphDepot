# -*- coding: utf-8 -*-
import morphdepot.config as config
from morphdepot.models.core import *
from morphdepot.models.morph import *
###########################
# Setting up the DB-session
###########################

engine = sa.create_engine(config.DB['url'], echo=config.DB['echo'])
if config.DB['type'] == "sqlite":
    print("preconfigure %s" %(config.DB['type']))
     # http://docs.sqlalchemy.org/en/rel_0_7/dialects/sqlite.html#foreign-key-support
    engine.execute("PRAGMA foreign_keys=ON")
elif config.DB['type'] == "postgresql":
    print("preconfigure %s" %(config.DB['type']))
    #results = engine.execute("SHOW search_path;")
    #for result in results:
    #    assert result[0] == config.DB['schema'], "search_path not set correctly"
    #results.close()
    if config.DB['pg_recreate_schema']:
        engine.execute("DROP SCHEMA %s CASCADE;" %(config.DB['schema']))
        engine.execute("CREATE SCHEMA %s;" %(config.DB['schema']))

Session = orm.sessionmaker(bind=engine)
Base.metadata.create_all(engine)
session = Session()

if config.DB['add_test_data']:

    ########
    # core #
    ########

    # Add Scientist
    # #############
    scientist = Scientist(
        first_name="Philipp",
        middle_name="Lothar",
        last_name="Rautenberg",
        affiliations=\
            "Ludwig-Maximilians-Universitaet Muenchen, Department Biology II, G-Node, Planegg-Martinsried, Germany"
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
    nr.tissue_sample = tissue
    session.commit()
    nr.neurons.append(neuron)
    session.commit()

    # File
    ######
    file_object = nr.add_file("init_db.py")
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
    session.add(GeneralParam(name='Param1'))
    seg.software = "SIGEN"
    seg.general_param = "Param1"
    session.commit()
