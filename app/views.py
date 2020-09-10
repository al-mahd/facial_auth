from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status
from facial_auth import settings

from rest_framework.decorators import api_view
from app.models import Student,ImageProfile
from app.serializers import StudentSerializer,ImageProfileSerializer
from rest_framework.decorators import api_view
from django.db.models.functions import Lower

from .forms import UploadFileForm
from django.core.files.storage import FileSystemStorage
import face_recognition
import numpy as np
import os
import PIL

# Create your views here.

###
# api to add new student
###
@api_view(['POST'])
def student_add(request):
    # add student
    req = JSONParser().parse(request)
    student_serializer = StudentSerializer(data=req)

    if not student_serializer.is_valid():
        return JsonResponse(student_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    student_serializer.save()        
    return JsonResponse(student_serializer.data, status=status.HTTP_201_CREATED)

###
# api to get 
# one student data
###
@api_view(['GET','PUT','DELETE'])
def student(request,id):
    # get student detail by id
    try: 
        student = Student.objects.get(pk=id) 
    except Student.DoesNotExist: 
        return JsonResponse({'message': 'The student does not exist'}, status=status.HTTP_404_NOT_FOUND) 
 
    # query detail by id
    if request.method == 'GET':
        student_serializer = StudentSerializer(student)
        return JsonResponse(student_serializer.data, status=status.HTTP_200_OK)

    return JsonResponse({}, status=status.HTTP_200_OK)

###
# api to add image 
# profile to student data &
# api to get one image
# profile data
###
@api_view(['POST','GET','PUT','DELETE'])
def image_profile(request,id):
    # get student detail by id
    try: 
        student = Student.objects.get(pk=id) 
    except Student.DoesNotExist: 
        return JsonResponse({'message': 'The student does not exist'}, status=status.HTTP_404_NOT_FOUND)
   
    # if request method is POST
    # add new image to student
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if not form.is_valid():  
            return JsonResponse({'message': 'invalid form'}, status=status.HTTP_400_BAD_REQUEST)

        tmp_file = request.FILES['file']

        fs = FileSystemStorage()
        filename = fs.save(tmp_file.name, tmp_file)
        uploaded_file_url = fs.url(filename)

        req = ImageProfile(student_id=id, filename=filename, url=uploaded_file_url)
        req.save()  

        return JsonResponse({'message': 'image uploaded'}, status=status.HTTP_201_CREATED)

    # if request method is GET
    # get image from student
    elif request.method == 'GET':
        try: 
            image_profile = ImageProfile.objects.get(student = student.id)
        except ImageProfile.DoesNotExist: 
            return JsonResponse({'message': 'The Image Profile does not exist'}, status=status.HTTP_404_NOT_FOUND) 

        image_profile_serializer = ImageProfileSerializer(image_profile)
        return JsonResponse(image_profile_serializer.data, status=status.HTTP_200_OK)
    
    # add update and delete
    ####

    return JsonResponse({}, status=status.HTTP_200_OK)

###
# api to validate image profile
# with current image profile 
# registered in db
###
@api_view(['POST'])
def validate_image_profile(request,nim):
    # get student detail by id
    try: 
        student = Student.objects.get(nim=nim) 
    except Student.DoesNotExist: 
        return JsonResponse({'message': 'The student does not exist'}, status=status.HTTP_404_NOT_FOUND)
   
    try: 
        image_profile = ImageProfile.objects.get(student = student.id)
    except ImageProfile.DoesNotExist: 
        return JsonResponse({'message': 'The Image Profile does not exist'}, status=status.HTTP_404_NOT_FOUND) 
    
    form = UploadFileForm(request.POST, request.FILES)
    if not form.is_valid():  
        return JsonResponse({'message': 'invalid form'}, status=status.HTTP_400_BAD_REQUEST)

    fs = FileSystemStorage()
    known_image,unknown_image = face_recognition.load_image_file(fs.open(image_profile.filename)), face_recognition.load_image_file(request.FILES['file'])

    known_image_encoding,unknown_encoding = face_recognition.face_encodings(known_image), face_recognition.face_encodings(unknown_image)
    if len(known_image_encoding) == 0 or len(unknown_encoding) == 0:
        return JsonResponse({"validate":False,"message":"one of image is empty"}, status=status.HTTP_200_OK)

    results = face_recognition.compare_faces([known_image_encoding[0]], unknown_encoding[0])
    if not all(results):
        return JsonResponse({"validate":False,"message":"both are not same person"}, status=status.HTTP_200_OK)

    return JsonResponse({"validate":True,"message":"both are same person"}, status=status.HTTP_200_OK)