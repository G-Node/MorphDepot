__author__ = 'philipp'

from django.contrib import admin
from django_morphdepot.morphdepot.models import *


class NeuronInline(admin.StackedInline):
    fields = ['label', 'type', 'microscope_slide']
    model = Neuron
    extra = 0


class MicroscopeSlideInline(admin.TabularInline):
    fields = ['label', 'animal']


class AnimalInline(admin.TabularInline):
    fields = ['label', 'species', 'age', 'age_uncertainty']
    model = Animal
    extra = 0
    inlines = [MicroscopeSlideInline]


class MicroscopeSlideAdmin(admin.ModelAdmin):
    fields = ['label', 'animal']
    inlines = [NeuronInline]


class AnimalAdmin(admin.ModelAdmin):
    fields = ['label', 'species', 'age', 'age_uncertainty']
    inlines = [MicroscopeSlideInline]


class ExperimenterAdmin(admin.ModelAdmin):
    fields = ['title', 'last_name', 'first_name', 'middle_name', 'affiliations', 'comment']
    list_display = ('fullname', 'affiliations', 'ctime', 'mtime')


class ExperimentAdmin(admin.ModelAdmin):
    fields = ['label', 'experimenter', 'date', 'lab_book_entry', 'comment']
    list_display = ('label', 'date', 'experimenter')
    inlines = [AnimalInline]


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



class FileFolderAdmin(admin.ModelAdmin):
    actions=['really_delete_selected']

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


class MicroscopeImageStackAdmin(admin.ModelAdmin):
    fields = ('label', 'microscope', 'microscope_slide', 'lense', 'zoom', 'laser_color', 'gain', 'laser_config',
        ('voxel_size_x', 'voxel_size_y', 'voxel_size_z'),
        )


admin.site.register(Experimenter, ExperimenterAdmin)
admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(MicroscopeSlide, MicroscopeSlideAdmin)
admin.site.register(Neuron)
admin.site.register(FileFolder, FileFolderAdmin)
admin.site.register(UploadedFile, UploadedFileAdmin)
admin.site.register(MicroscopeImageStack, MicroscopeImageStackAdmin)
#admin.site.register(Animal, AnimalAdmin)