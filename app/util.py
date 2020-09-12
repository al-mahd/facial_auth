from PIL import Image
import urllib.request
from django.core.files.storage import FileSystemStorage
import uuid

def handle_uploaded_file(f):
    with open('name.jpg', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def handle_download_file(URL):
    name = "{}.jpg".format(uuid.uuid4())
    fs = FileSystemStorage()
    with urllib.request.urlopen(URL) as url:
        name = fs.save(name, url)
        if name:
            return fs.open(name)