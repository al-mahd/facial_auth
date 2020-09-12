from django.db import models
from django.core.files.storage import FileSystemStorage
import uuid

# Create your models here.
class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nim = models.CharField(max_length=70, blank=False, default='')
    name = models.TextField(blank=False, default='')
    status = models.IntegerField(blank=False, default=0)

class ImageProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, default=1, verbose_name="Student", on_delete=models.SET_DEFAULT)
    url = models.TextField(blank=False, default='')   

class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, default=1, verbose_name="Student", on_delete=models.SET_DEFAULT)
