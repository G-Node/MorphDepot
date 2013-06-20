class Identifiable(object):
    """
    .. note:: mixture of "Entity" and "Serializable". Alternativ: "IDataType"?
    """
    def id(self, *args, **kwargs):
        raise NotImplementedError
    def ctime(self, *args, **kwargs):
        raise NotImplementedError
    def mtime(self, *args, **kwargs):
        raise NotImplementedError
    def get_yaml(self, *args, **kwargs):
        raise NotImplementedError
    def set_by_yaml(self, *args, **kwargs):
        raise NotImplementedError
    def get_json(self, *args, **kwargs):
        raise NotImplementedError
    def set_by_json(self, *args, **kwargs):
        raise NotImplementedError
    def get_xml(self, *args, **kwargs):
        raise NotImplementedError
    def set_by_xml(self, *args, **kwargs):
        raise NotImplementedError


class Dimensionable(object):
    def name(self, *args, **kwargs):
        raise NotImplementedError
    def description(self, *args, **kwargs):
        raise NotImplementedError
    def comment(self, *args, **kwargs):
        raise NotImplementedError
