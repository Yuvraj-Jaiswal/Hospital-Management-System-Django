from rest_framework import serializers
from .models import Doctor, Patient, PDates


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'


class PDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDates
        fields = '__all__'
