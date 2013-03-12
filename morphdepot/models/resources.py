__author__ = 'philipp'

# from base import Base
from identity import Identity

import sqlalchemy as sa
import sqlalchemy.orm as orm

class Scientist(Identity):
    __tablename__ = "scientists"
    __mapper_args__ = {'polymorphic_identity': 'Scientist'}
    uuid = sa.Column(sa.ForeignKey('identities.uuid'), primary_key=True)
    first_name = sa.Column(sa.String(64), nullable=False)
    middle_name = sa.Column(sa.String(64))
    last_name = sa.Column(sa.String(64), nullable=False)
    title = sa.Column(sa.String(64))
    affiliations = sa.Column(sa.String(128), nullable=False)

class Experiment(Identity):
    __tablename__ = "experiments"
    __mapper_args__ = {'polymorphic_identity': 'Experiment'}
    uuid = sa.Column(sa.ForeignKey('identities.uuid'), primary_key=True)
    label = sa.Column(sa.String(64), nullable=False, unique=True)
    date = sa.Column(sa.DateTime, nullable=False)
    lab_book_entry = sa.Column(sa.Text)
    scientist_uuid = sa.Column(sa.ForeignKey('scientists.uuid'))

    # Properties
    scientist = orm.relationship("Scientist", backref="experiments")
