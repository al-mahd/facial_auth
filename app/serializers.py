from rest_framework import serializers 
from app.models import Student,ImageProfile

 # Create your model serializer here.
class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ('id', 'nim', 'name', 'status')

class ImageProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageProfile
        fields = ('id', 'student_id','url')        