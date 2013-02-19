import hashlib, os

from django.db import models
from django_extensions.db.fields import UUIDField
from django.core.files.storage import default_storage
from django.conf import settings

import utils

"""
Short UUID-Doku:
http://david.feinzeig.com/blog/2012/03/01/how-to-add-a-uuid-field-in-django-using-django-extensions-and-how-to-make-it-a-read-only-admin-field/
"""

#######################
# MorphDepot - Metadata
#######################

class Identity(models.Model):
    uuid = UUIDField(primary_key=True, version=4)
    ctime = models.DateTimeField('created', auto_now_add=True, blank=False)
    mtime = models.DateTimeField('modified', auto_now=True, blank=False)
    comment = models.TextField(default="", blank=True)

    class Meta:
        abstract = True


class MicroscopeConfig(models.Model):
    zoom = models.DecimalField(max_digits=5, decimal_places=2)
    lense = models.DecimalField(max_digits=5, decimal_places=2)
    gain = models.DecimalField(max_digits=5, decimal_places=2)
    laser_color = models.CharField(max_length=64)
    laser_config = models.CharField('e.g. gain/time/percentage', max_length=64)
    voxel_size_x = models.DecimalField('x [nm] (voxel-size)', max_digits=7, decimal_places=2)
    voxel_size_y = models.DecimalField('y [nm] (voxel-size)', max_digits=7, decimal_places=2)


    class Meta:
        abstract = True


class Scientist(Identity):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    middle_name = models.CharField(max_length=64, blank=True)
    title = models.CharField(max_length=16, blank=True)
    affiliations = models.CharField(max_length=128, blank=True)

    def __unicode__(self):
        return self.fullname

    @property
    def fullname(self):
        return u"%s %s %s" % (self.title, self.first_name, self.last_name)


class AnimalType(Identity):
    notation = models.CharField(unique=True, max_length=64)

    def __unicode__(self):
        return self.notation


class Animal(Identity):
    label = models.CharField(unique=True, max_length=64)
    animal_type = models.ForeignKey(AnimalType)
    age = models.BigIntegerField("age in days [P]") #age in days
    age_uncertainty = models.CharField(max_length=64, blank=True)

    def __unicode__(self):
        return self.label



class Experiment(Identity):
    label = models.CharField(unique=True, max_length=64)
    date = models.DateField()
    scientist = models.ForeignKey(Scientist)
    animal = models.OneToOneField(Animal)
    lab_book_entry = models.TextField()

    def __unicode__(self):
        return self.label


class MicroscopeSlide(Identity):
    label = models.CharField(unique=True, max_length=64)
    experiment = models.ForeignKey(Experiment)

    def __unicode__(self):
        return self.label


class NeuronType(Identity):
    type = models.CharField(unique=True, max_length=64)

    def __unicode__(self):
        return self.type


class Neuron(Identity):
    label = models.CharField(unique=True, max_length=64)
    type = models.ForeignKey(NeuronType)
    microscope_slide = models.ForeignKey(MicroscopeSlide)

    def __unicode__(self):
        return self.label


#####################
# MorphDepot Raw Data
#####################

# File(folder) Upload

class FileFolder(Identity):
    label = models.CharField(unique=True, max_length=64)
    checksum = models.CharField(max_length=64)
    path = models.CharField(max_length=256)

    def save(self, *args, **kwargs):
        super(FileFolder, self).save(*args, **kwargs)
        hash = hashlib.sha1()
        for file in self.uploadedfile_set.all():
            hash.update(file.checksum)
        self.checksum = hash.hexdigest()
        self.path = os.path.join(utils.ROOT_FILEFOLDERS, self.uuid)
        super(FileFolder, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        for file in self.uploadedfile_set.all():
            file.delete()
        os.rmdir(os.path.join(settings.MEDIA_ROOT, self.path))
        super(FileFolder, self).delete(*args, **kwargs)

    @property
    def n_files(self):
        return len(self.uploadedfile_set.all())

    def __unicode__(self):
        return "%s with %s files" %(self.path, self.n_files)


class UploadedFile(models.Model):
    file = models.FileField(upload_to=utils.get_upload_path)
    filefolder = models.ForeignKey(FileFolder)
    filesize = models.PositiveIntegerField(blank=True, null=True, editable=False)
    checksum = models.CharField(max_length=32, blank=True, editable=False)

    class Meta:
        ordering = ['file']

    def save(self, *args, **kwargs):
        print "********************* in save *************************"
        super(UploadedFile, self).save(*args, **kwargs)
        f = default_storage.open(self.file, 'rb')
        hash = hashlib.sha1()
        if f.multiple_chunks():
            for chunk in f.chunks():
                hash.update(chunk)
        else:
            hash.update(f.read())
        f.close()
        self.checksum =  hash.hexdigest()
        self.filesize = self.file.size
        super(UploadedFile, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        print "********************* in delete *************************"
        # You have to prepare what you need before delete the model
        storage, path = self.file.storage, self.file.path
        filefolder = self.filefolder
        print filefolder.uploadedfile_set.all()
        print filefolder.uuid
        # Delete the model before the file
        super(UploadedFile, self).delete(*args, **kwargs)
        print filefolder
        print filefolder.uploadedfile_set.all()
        filefolder.save()
        print filefolder.uploadedfile_set.all()
        # Delete the file after the model
        storage.delete(path)

    def __unicode__(self):
        filename = os.path.basename(self.file.name)
        return filename


# Raw data classes

class DigitalNeuronRepresentation(FileFolder):
    neurons = models.ManyToManyField(Neuron, through='Neuron_DigitalNeuronRepresentation_Maps')


class Neuron_DigitalNeuronRepresentation_Maps(models.Model):
    neuron = models.ForeignKey(Neuron)
    digital_neural_representation = models.ForeignKey(DigitalNeuronRepresentation)


class Microscope(Identity):
    label = models.CharField(max_length=64)


class MicroscopeImageStack(DigitalNeuronRepresentation, MicroscopeConfig):
    microscope = models.ForeignKey(Microscope)
    voxel_size_z = models.DecimalField('z [nm] (voxel-size)', max_digits=7, decimal_places=2)


class MicroscopeImage(DigitalNeuronRepresentation, MicroscopeConfig):
    microscope = models.ForeignKey(Microscope)


class Segmentation(DigitalNeuronRepresentation):
    # neurons = models.ManyToManyField(Neuron, through='Neuron_DigitalNeuronRepresentation_Maps')
    dye = models.CharField(max_length=64)
    method = models.TextField()


class SegmentationSigen(Segmentation):
    d_parameter = models.DecimalField(max_digits=5, decimal_places=2)
    v_parameter = models.DecimalField(max_digits=5, decimal_places=2)
    c_parameter = models.DecimalField(max_digits=5, decimal_places=2)
    s_parameter = models.DecimalField(max_digits=5, decimal_places=2)


class MicroscopeImageStackMDP(MicroscopeImageStack):
    information = models.TextField()