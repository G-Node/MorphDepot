__author__ = 'philipp'

from django.contrib import admin
from django_morphdepot.morphdepot.models import *


########################
# Experimental Meta-Data
########################
class NeuronAdmin(admin.ModelAdmin):
    fields = ['label', 'type', 'microscope_slide', 'comment']


class NeuronInline(admin.StackedInline):
    fields = ['label', 'type', 'microscope_slide']
    model = Neuron
    extra = 0


class NeuronTypeAdmin(admin.ModelAdmin):
    fields = ['label', 'comment']


class MicroscopeAdmin(admin.ModelAdmin):
    fields = ['label', 'comment']

class MicroscopeSlideInline(admin.TabularInline):
    # Todo: improve integration within ExperimentAdmin
    fields = ['label', 'comment']
    model = MicroscopeSlide
    extra = 0


class AnimalInline(admin.TabularInline):
    fields = ['label', 'species', 'age', 'age_uncertainty']
    model = Animal
    extra = 0
    inlines = [MicroscopeSlideInline]


class MicroscopeSlideAdmin(admin.ModelAdmin):
    fields = ['label', 'experiment', 'comment']


class AnimalAdmin(admin.ModelAdmin):
    fields = ['label', 'age', 'animal_type', 'age_uncertainty', 'comment']
    list_display = ('ctime', 'mtime', 'comment')
    # inlines = [MicroscopeSlideInline]


class AnimalTypeAdmin(admin.ModelAdmin):
    fields = ['label', 'comment']


class ScientistAdmin(admin.ModelAdmin):
    fields = ['title', 'last_name', 'first_name', 'middle_name', 'affiliations', 'comment']
    list_display = ('fullname', 'affiliations', 'ctime', 'mtime')


class ExperimentAdmin(admin.ModelAdmin):
    fields = ['label', 'scientist', 'animal', 'date', 'lab_book_entry', 'comment']
    list_display = ('label', 'date', 'scientist')
    inlines = [MicroscopeSlideInline]


#############
# File Upload
#############

class UploadedFileAdmin(admin.ModelAdmin):
    actions=['really_delete_selected']

    def get_actions(self, request):
        actions = super(UploadedFileAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def really_delete_selected(self, request, queryset):
        for obj in queryset:
            obj.delete()

        if queryset.count() == 1:
            message_bit = "1 uploaded file was"
        else:
            message_bit = "%s uploded files were" % queryset.count()
        self.message_user(request, "%s successfully deleted." % message_bit)
    really_delete_selected.short_description = "Delete selected entries"


class UploadedFilesInline(admin.TabularInline):
    # fields = ['filefolder', 'file']
    model = UploadedFile
    extra = 0


class UploadedFileInline(admin.TabularInline):
    # fields = ['filefolder', 'file']
    model = UploadedFile
    max_num = 1
    extra = 0


class FileFolderAdmin(admin.ModelAdmin):
    actions=['really_delete_selected']
    inlines = [UploadedFilesInline]
    fields = ['label', 'comment']
    list_display = ['path', 'checksum', 'mtime', 'ctime']

    def get_actions(self, request):
        actions = super(FileFolderAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def really_delete_selected(self, request, queryset):
        for obj in queryset:
            obj.delete()

        if queryset.count() == 1:
            message_bit = "1 folder was"
        else:
            message_bit = "%s folders were" % queryset.count()
        self.message_user(request, "%s successfully deleted." % message_bit)
    really_delete_selected.short_description = "Delete selected entries"


########################
# Digital Representation
########################

# toOne
class NeuronDNRInline(admin.TabularInline):
    verbose_name = "Neuron" # see also: 'related_name' at Neuron_DigitalNeuronRepresentation_Maps
    verbose_name_plural = "Related Neuron"
    max_num = 1
    model = Neuron_DigitalNeuronRepresentation_Maps
    extra = 1

# toMany
class NeuronsDNRInline(admin.TabularInline):
    verbose_name = "Neuron" # see also: 'related_name' at Neuron_DigitalNeuronRepresentation_Maps
    verbose_name_plural = "Related Neurons"
    model = Neuron_DigitalNeuronRepresentation_Maps
    extra = 0


class DigitalNeuronRepresentationAdmin(admin.ModelAdmin):
    verbose_name = "test"
    fields = ['label']
    inlines = [NeuronDNRInline]


class SegmentationAdmin(admin.ModelAdmin):
    fields = ['label', 'filefolder', 'comment']
    inlines = [NeuronDNRInline]


class SegmentationSigenAdmin(admin.ModelAdmin):
    fields = ['label', 'd_parameter', 'v_parameter', 'c_parameter', 's_parameter']
    inlines = [NeuronDNRInline]


class MicroscopeImageStackAdmin(admin.ModelAdmin):
    fields = ('label', 'microscope', 'lense', 'zoom', 'laser_color', 'gain', 'laser_config',
        ('voxel_size_x', 'voxel_size_y', 'voxel_size_z'),
        )
    inlines = [NeuronsDNRInline]


admin.site.register(Scientist, ScientistAdmin)
admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(Microscope, MicroscopeAdmin)
admin.site.register(MicroscopeSlide, MicroscopeSlideAdmin)
admin.site.register(Neuron, NeuronAdmin)
admin.site.register(NeuronType, NeuronTypeAdmin)
admin.site.register(FileFolder, FileFolderAdmin)
admin.site.register(UploadedFile, UploadedFileAdmin)
admin.site.register(MicroscopeImageStack, MicroscopeImageStackAdmin)
admin.site.register(Animal, AnimalAdmin)
admin.site.register(AnimalType, AnimalTypeAdmin)
#admin.site.register(DigitalNeuronRepresentation, DigitalNeuronRepresentationAdmin)
admin.site.register(Segmentation, SegmentationAdmin)
admin.site.register(SegmentationSigen, SegmentationSigenAdmin)
