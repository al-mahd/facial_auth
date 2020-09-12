from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status
from facial_auth import settings

from rest_framework.decorators import api_view
from app.models import Student,ImageProfile,Session
from app.serializers import StudentSerializer,ImageProfileSerializer
from rest_framework.decorators import api_view
from django.db.models.functions import Lower

from .forms import UploadFileForm
from django.core.files.storage import FileSystemStorage
import face_recognition
import numpy as np
import os
import PIL
import uuid
from .util import handle_download_file

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
def student(request,nim):
    # get student detail by id
    try: 
        student = Student.objects.get(nim=nim) 
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
        req = JSONParser().parse(request)
        uploaded_file_url = req['url']

        req = ImageProfile(student_id=id, url=uploaded_file_url)
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
def validate_image_profile(request,id):
    try: 
        image_profile = ImageProfile.objects.get(student = id)
    except ImageProfile.DoesNotExist: 
        return JsonResponse({'message': 'The Image Profile does not exist'}, status=status.HTTP_404_NOT_FOUND) 
    
    form = UploadFileForm(request.POST, request.FILES)
    if not form.is_valid():  
        return JsonResponse({'message': 'invalid form'}, status=status.HTTP_400_BAD_REQUEST)

    response_data = {"validate":True,"message":"both are same person","session_id":""}

    fs = FileSystemStorage()
    in_file = request.FILES['file']
    # fs.save(in_file.name,in_file)

    temp_name = handle_download_file(image_profile.url)

    known_image,unknown_image = face_recognition.load_image_file(fs.open(temp_name)), face_recognition.load_image_file(in_file)
    known_image_encoding,unknown_encoding = face_recognition.face_encodings(known_image), face_recognition.face_encodings(unknown_image)
    if len(known_image_encoding) == 0 or len(unknown_encoding) == 0:
        # print("unknown image : {} ,known image : {} ".format(len(unknown_encoding),len(known_image_encoding)))
        response_data["validate"] = False
        response_data["message"] = "one of image is empty"
        return JsonResponse(response_data, status=status.HTTP_200_OK)

    results = face_recognition.compare_faces([known_image_encoding[0]], unknown_encoding[0])
    if not all(results):
        response_data["validate"] = False
        response_data["message"] = "both are not same person"
        return JsonResponse(response_data, status=status.HTTP_200_OK)
    
    session = Session(student = student)
    # session.save()

    response_data["session_id"] =  session.id
    # fs.delete(temp_name)

    return JsonResponse(response_data, status=status.HTTP_200_OK)


###
# api to get or delete session
###
@api_view(['GET','DELETE'])
def session(request,id):
    # get session detail by id
    try: 
        session = Session.objects.get(pk=id) 
    except Session.DoesNotExist: 
        return JsonResponse({'message': 'The session does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        student = Student.objects.get(pk=session.student.id)
        return JsonResponse(student.data, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        session.delete()
        return JsonResponse({'message': 'The session hass been deleted'}, status=status.HTTP_200_OK)

    return JsonResponse({}, status=status.HTTP_200_OK)