# -*- coding: utf-8 -*-
import datetime as dt
import uuid as uuid_package
import sqlalchemy as sa
from sqlalchemy import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import declared_attr
from morphdepot.models import Base
from morphdepot.models.utils.interfaces import Identifiable

__author__ = 'Philipp Rautenberg'


class DimensionMixin(object):
    name = sa.Column('name', sa.String, primary_key=True)
    description = sa.Column('description', sa.String)
    comment = sa.Column('comment', sa.Text)

    def __init__(self, name, description=None, comment=None):
        """Dimension with following parameters:
        :param name: string
        :param description: string
        :param comment: text
        """
        Base.__init__(self, name=name, description=description, comment=comment)


class IDMixin(object):
    """
    This mixin is just used to facilitate inheritance behavior (from joined table to something else)
    """
    @declared_attr
    def id(cls):
        return sa.Column(sa.ForeignKey('identities.id'), primary_key=True)


class UUID(TypeDecorator):
    """Platform-independent UUID type.

    Uses Postgresql's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid_package.UUID):
                return "%.32x" % uuid_package.UUID(value)
            else:
                # hexstring
                return "%.32x" % value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid_package.UUID(value)


class UUIDMixin(object):
    id = sa.Column('id', UUID, default=uuid_package.uuid4, primary_key=True)


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

    @staticmethod
    def update_mtime(mapper, connection, target):
        target.mtime = dt.datetime.now()

    @classmethod
    def __declare_last__(cls):
        sa.event.listen(cls, 'before_update', cls.update_mtime)


