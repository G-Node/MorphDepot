#!/usr/bin/env python -3 -t
# -*- coding: utf-8 -*-

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


class Arborization_Area(DimensionMixin, Base):
    __tablename__ = 'arborization_areas'


class CellBodyRegion(DimensionMixin, Base):
    __tablename__ = 'cell_body_regions'


class Axonal_Tract(DimensionMixin, Base):
    __tablename__ = 'axonal_tracts'