# -*- coding: utf-8 -*-
__author__ = 'Philipp Rautenberg'

import sqlalchemy as sa
from sqlalchemy import orm

from morphdepot.models.core import NeuroRepresentation, Scientist
from morphdepot.models.dimensions import *

class MicroscopeImage(NeuroRepresentation):
    __tablename__ = 'microscope_images'
    __mapper_args__ = {'polymorphic_identity': 'MicroscopeImage'}
    id = sa.Column(sa.ForeignKey('neuro_representations.id'), primary_key=True)


class MicroscopeImageStack(NeuroRepresentation):
    __tablename__ = 'microscope_image_stacks'
    __mapper_args__ = {'polymorphic_identity': 'MicroscopeImageStack'}
    id = sa.Column(sa.ForeignKey('neuro_representations.id'), primary_key=True)


# Table to enable n:m-mapping for Segmentation and GeneralParam
segmentation__general_param__maps = sa.Table(
    'segmentation__general_param__maps',
    Base.metadata,
    sa.Column('segmentation_id', sa.ForeignKey('segmentations.id'), primary_key=True),
    sa.Column('general_param_name', sa.ForeignKey('general_param.name'), primary_key=True))


class Segmentation(NeuroRepresentation):
    __tablename__ = 'segmentations'
    __mapper_args__ = {'polymorphic_identity': 'Segmentation'}
    id = sa.Column(sa.ForeignKey('neuro_representations.id'), primary_key=True)
    microscope_image_stack_id = sa.Column(
        sa.ForeignKey('microscope_image_stacks.id'),
        nullable=False)
    arguments = sa.Column(sa.String)
    quality_rank = sa.Column(sa.Integer)
    operator = sa.Column(sa.ForeignKey('scientists.id'))
    # Dimensions:
    software = sa.Column(sa.ForeignKey(Software.name))

    # References
    microscope_image_stack = orm.relationship(
        'MicroscopeImageStack',
        primaryjoin=(microscope_image_stack_id == MicroscopeImageStack.id),
        backref='segmentation',
        )
    general_params = orm.relatinoship(
        "GeneralParam",
        secondary=segmentation__general_param__maps,
        backref="general_params"
    )
