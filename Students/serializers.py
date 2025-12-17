from rest_framework import serializers
from .models import StudentTable

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentTable
        fields = ['id', 'name', 'age']
