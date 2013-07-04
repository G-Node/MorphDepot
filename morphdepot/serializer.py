"""
Method(s) to serialize / reconstruct model objects from YAML structures.

"""
import yaml
import sqlalchemy as sa


class Serializer(object):
    """
    An abstract class used for parsing YAML -> Python object and vice versa.
    """

    @classmethod
    def deserialize(cls, model, yaml_string):
        """
        Instantiates a new python object from a given YAML representation.

        :param cls:         Serializer class
        :param model:       model class to instantiate a new object
        :param yaml_string: a YAML string representaion of an object

        """
        yaml_obj = yaml.load(yaml_string)
        obj = model()

        for column in obj.__mapper__.columns:
            name = column.name

            if name in yaml_obj and cls.is_deserializable(column):
                setattr(obj, name, yaml_obj[name])

        return obj

    @classmethod
    def serialize(cls, obj):
        """ 
        Produces a YAML representation from a given python object. An object 
        should inherit from SQLAlchemy base class.

        :param obj:         python object to serialize

        """
        yaml_obj = {}

        for column in obj.__mapper__.columns:

            if cls.is_serializable(column):
                # do not serialize reserved attributes. serialize only 
                # string-based foreign keys, related to simple dimensions. 
                # normally these are string-typed
                continue

            name = column.name
            yaml_obj[name] = getattr(obj, name)

        return yaml.dump(yaml_obj)

    @classmethod
    def is_serializable(cls, column):
        """ with this method one can filter reserved columns """
        foreign_key = len(column.foreign_keys) > 0

        if foreign_key and not column.type.__class__ == sa.String:
            return False
        return True

    @classmethod
    def is_deserializable(cls, column):
        """ with this method one can filter reserved columns """
        foreign_key = len(column.foreign_keys) > 0

        if column.name in ['id', 'mtime', 'ctime', 'dto_type'] or \
            (foreign_key and not column.type.__class__ == sa.String):
            return False

        return True
