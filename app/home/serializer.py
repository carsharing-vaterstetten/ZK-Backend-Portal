from rest_framework import serializers
from .models import Cards, Firmware, Cars, Logs
from django.utils import timezone

class CardSerializer(serializers.ModelSerializer):
    id = serializers.CharField(required=False, write_only=True)
    class Meta:
        model = Cards
        fields = '__all__'

class FirmwareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Firmware
        fields = '__all__'
    firmware_data = serializers.FileField()

class CarsSerializer(serializers.ModelSerializer):
    frimware_verison = FirmwareSerializer()
    class Meta:
        model = Cars
        fields = '__all__'
    
    def update(self, instance, validated_data):
        firmware_data = validated_data.pop('firmware_version', None)
        if firmware_data:
            firmware_instance, created = Firmware.objects.get_or_create(version=firmware_data['version'], defaults=firmware_data)
            instance.firmware_version = firmware_instance
        instance.license_plate = validated_data.get('license_plate', instance.license_plate)
        instance.mac_address = validated_data.get('mac_address', instance.mac_address)
        instance.save()
        return instance

class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logs
        fields = ['uploaded_by', 'created_at', 'firmware_version', 'log']
