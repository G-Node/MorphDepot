import uuid as uuid_package

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr

from morphdepot.models.utils.uuid_type import UUID


class UUIDMixin(object):
    id = sa.Column('id', UUID, default=uuid_package.uuid4, primary_key=True)


class DimensionMixin(object):
    name = sa.Column('name', sa.String, primary_key=True)
    description = sa.Column('description', sa.String)
    comment = sa.Column('comment', sa.Text)


class IDMixin(object):
    """
    This mixin is just used to facilitate inheritance behavior (from joined table to something else)
    """
    @declared_attr
    def id(cls):
        return sa.Column(sa.ForeignKey('identities.id'), primary_key=True)

