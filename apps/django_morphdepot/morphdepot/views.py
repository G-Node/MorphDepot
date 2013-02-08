# Create your views here.
from django import http
import json
from django import forms
from django.shortcuts import render_to_response
from django.http import HttpResponse

#import django_morphdepot
from django_morphdepot.morphdepot.models import FileFolder, UploadedFile

#PR: storage
import os
import hashlib
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
######


class SimpleFileForm(forms.Form):
    file = forms.Field(widget=forms.FileInput, required=False)


def add_filefolder(file_list, subfolder=""):
    file_list.sort(key=str) #PR: sort list by file names
    #rel_path_folder = os.path.join(FILEFOLDER, subfolder)
    new_file_folder = FileFolder()
    new_file_folder.save() #PR; save to generate uuid

    folder_sha1 = hashlib.sha1()
    for form_file in file_list:#request.FILES.getlist('form_files'):
        file = UploadedFile()
        file.filefolder = new_file_folder
        file.file = form_file
        file.save()
        folder_sha1.update(file.checksum)
    print folder_sha1.hexdigest()
    #new_file_folder.checksum = folder_sha1.hexdigest()
    new_file_folder.save()
    return new_file_folder


def directupload(request):
    """
    Saves the file directly from the request object.
    Disclaimer:  This is code is just an example, and should
    not be used on a real website.  It does not validate
    file uploaded:  it could be used to execute an
    arbitrary script on the server.
    """
    template = 'fileupload.html'

    if request.method == 'POST':
        #print request.FILES
        #if form.is_valid():
        add_filefolder(request.FILES.getlist('form_files'))
        # Redirect to the document list after POST
        return HttpResponse("OK") #Redirect(reverse('django_morphdepot.views.directupload'))
    else:
        # display the form
        form = SimpleFileForm()
        return render_to_response(template)

class UploadImageStack(forms.Form):
    label = forms.CharField(max_length=64)
    file = forms.FileField()

def upload_imagestacks(request):
    pass