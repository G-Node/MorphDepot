__author__ = 'philipp'


import os, hashlib

ROOT_FILEFOLDERS = 'FileFolders'

def get_upload_path(instance, filename):
    return os.path.join(
        ROOT_FILEFOLDERS, instance.filefolder.uuid, filename)


def add_delete_on_delete(cls):
    """
    Source: http://djangosnippets.org/snippets/2782/
    """
    def delete(self, *args, **kwargs):
        # You have to prepare what you need before delete the model
        storage, path = self.file.storage, self.file.path
        filefolder = self.filefolder
        print filefolder.uploadedfile_set.all()
        print filefolder.uuid
        # Delete the model before the file
        super(cls, self).delete(*args, **kwargs)
        print filefolder
        print filefolder.uploadedfile_set.all()
        filefolder.save()
        print filefolder.uploadedfile_set.all()
        # Delete the file after the model
        storage.delete(path)
    cls.delete = delete
    return cls


"""
UUIDField, source: http://djangosnippets.org/snippets/335/

not used anymore (now: from django_extensions.db.fields import UUIDField)
"""
