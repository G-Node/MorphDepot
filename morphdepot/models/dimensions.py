from __future__ import division, unicode_literals, print_function

from morphdepot.models import Base
from morphdepot.models.utils.beanbags import DimensionMixin

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


class ArborizationArea(DimensionMixin, Base):
    __tablename__ = 'arborization_areas'


class CellBodyRegion(DimensionMixin, Base):
    __tablename__ = 'cell_body_regions'


class AxonalTract(DimensionMixin, Base):
    __tablename__ = 'axonal_tracts'


# morph
class Software(DimensionMixin, Base):
    __tablename__ = 'softwares'


class GeneralParam(DimensionMixin, Base):
    __tablename__ = 'general_params'


# ephys
class ResponseProperty(DimensionMixin, Base):
    __tablename__ = 'response_properties'


class SpontaneousActivity(DimensionMixin, Base):
    __tablename__ = 'spontaneous_activities'


all_dimensions = [AnimalSpecies, Company, LaborState, Colony, NeuronCategory,\
    ArborizationArea, CellBodyRegion, AxonalTract, Software, GeneralParam, \
        ResponseProperty, SpontaneousActivity]
