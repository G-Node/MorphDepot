import sqlalchemy as sa
import uuid as uuid_package
from morphdepot.sa.uuid_type import UUID

class UUIDMixin(object):
    id = sa.Column('id', UUID, default=uuid_package.uuid4, primary_key=True)


class DimensionMixin(object):
    name = sa.Column('name', sa.String, primary_key=True)
    description = sa.Column('description', sa.String)
    comment = sa.Column('comment', sa.Text)
