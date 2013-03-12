__author__ = 'philipp'

import datetime as dt
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.associationproxy import association_proxy

from base import Base
from uuid_type import UUIDMixin


identity_tag_maps = sa.Table(
    'identity_tag_maps',
    Base.metadata,
    sa.Column('identity_uuid', sa.ForeignKey('identities.uuid'), primary_key=True),
    sa.Column('tag_uuid', sa.ForeignKey('tags.uuid'), primary_key=True))

def find_or_create_tag(kw):
    tag = Tag.query.filter_by(name=kw).first()
    if not(tag):
        tag = Tag(name=kw)
        # if aufoflush=False used in the session, then uncomment below
        if not hasattr(Tag, "session"):
            Tag.session = DBSession()
        Tag.session.add(tag)
        Tag.session.flush()
    return tag


class Tag(UUIDMixin, Base):
    __tablename__ = 'tags'
    name = sa.Column(sa.String, unique=True, nullable=False)

    def __init__(self, name):
        self.name = name


class Identity(UUIDMixin, Base):
    __tablename__ = 'identities'
    mtime = sa.Column(
        'mtime',
        sa.DateTime,
        default=dt.datetime.now())
    ctime = sa.Column(
        'ctime',
        sa.DateTime,
        default=dt.datetime.now())
    _dto_type = sa.Column('dto_type', sa.String, nullable=False)
    __mapper_args__ = {'polymorphic_on': _dto_type}


    # tags & proxy the 'keyword' attribute from the 'kw' relationship
    tag_objects = orm.relationship('Tag',
        secondary=identity_tag_maps,
        backref='tagged')
    tags = association_proxy('tag_objects', 'name',
        creator=find_or_create_tag)
