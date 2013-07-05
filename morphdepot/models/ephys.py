# -*- coding: utf-8 -*-
__author__ = 'Philipp Rautenberg'

import sqlalchemy as sa
from sqlalchemy import orm

from morphdepot.models.core import NeuroRepresentation
from morphdepot.models import Base

electrophysiology__response_property__maps = sa.Table(
    'electrophysiology_response_property_maps',
    Base.metadata,
    sa.Column('electrophysiology_id', sa.ForeignKey('electrophysiologies.id'), primary_key=True),
    sa.Column('response_property_name', sa.ForeignKey('response_properties.name'), primary_key=True)
)

class Electrophysiology(NeuroRepresentation):
    __tablename__ = 'electrophysiologies'
    __mapper_args__ = {'polymorphic_identity': 'Electrophysiology'}

    id = sa.Column(sa.ForeignKey('neuro_representations.id'), primary_key=True)
    spontaneous_activity = sa.Column(sa.ForeignKey('spontaneous_activities.name'))
    quality_rank = sa.Column(sa.Integer)
    stim_pulse_frequency = sa.Column(sa.Float)
    stim_vibration_frequency = sa.Column(sa.Float)
    data_acquisition_sampling_frequency = sa.Column(sa.Float)
    data_acquisition_voltage_range = sa.Column(sa.Float)
    response_property_name = sa.Column(sa.ForeignKey('response_properties.name'))

    # many-to-many: Electrophysiology <-> ResponseProperties
    response_properties = orm.relationship(
        "ResponseProperty",
        secondary=electrophysiology__response_property__maps,
        backref='electrophysiologies'
    )

    def __init__(self, *args, **kwargs):
        """Electrophysiology

        :param label: String(64)
        :param spontaneous_activity: String
        :param quality_rank: Integer
        :param stim_pulse_frequency: Float
        :param stim_vibration_frequency: Float
        :param data_acquisition_sampling_frequency: Float
        :param data_acquisition_voltage_range: Float
        :param tissue_sample: TissueSample
        :param response_properties: List of ResponseProperty
        """
        Base.__init__(self, *args, **kwargs)

    def __str__(self):
        return self.label

    def __repr__(self):
        return "Electrophysiology(%r, %r, %r, %r, %r, %r, %r)" %(
               self.label,
               self.spontaneous_activity,
               self.quality_rank,
               self.stim_pulse_frequency,
               self.stim_vibration_frequency,
               self.data_acquisition_sampling_frequency,
               self.data_acquisition_voltage_range,
        )
