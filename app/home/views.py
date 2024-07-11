from django.http import FileResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView, RetrieveAPIView
from rest_framework.mixins import UpdateModelMixin, CreateModelMixin
from rest_framework.permissions import IsAdminUser
from .serializer import CardSerializer, CarsSerializer, FirmwareSerializer
from .models import Cards, Cars, Firmware
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
# Create your views here.

class CardsCreateList(CreateModelMixin, ListAPIView):
    serializer_class = CardSerializer
    queryset = Cards.objects.all()
    permission_classes = (IsAdminUser, )

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,status=status.HTTP_201_CREATED, headers=headers)


class CheckFirmware(APIView):
    def post(self, request, *args, **kwargs):               
        firmware_version = request.data.get('firmware_version')
        firmware = Firmware.objects.filter(version=firmware_version).first()
        # Wenn der Firmware version nicht in Database ist, dann soll eine Fehlermeldung kommen
        # Immer wenn eine neue Firmware Version für Arduino gebuildet wird muss diese gleich in dar Datenbank eingetragen werden!!!
        if not firmware:
            return Response({'message': 'Firmware not found'}, status=status.HTTP_404_NOT_FOUND)
        mac_address = request.data.get('mac_address')
        car = Cars.objects.filter(mac_address=mac_address).first()
        # Wenn das Auto nicht in der Datenbank ist, dann soll diese in Datenbank mit der Aktuelle Firmware Version eingetragen werden
        if not car:
            car = Cars.objects.create(mac_address=mac_address, firmware_version=firmware, license_plate='UNBEKANNT')
            return Response({'message': 'Car added to database'}, status=status.HTTP_201_CREATED)

        # Wenn das Auto gleiche Version hat, wie in der Datenbank pflegt dann soll nichts gemacht werden
        if car.firmware_version_id == firmware.id:
            return Response({'message': 'No updatet needed'}, status=status.HTTP_200_OK) 
        # Die Binary Daten von frimware_file als Response zurückgeben
        new_firmware = Firmware.objects.filter(id=car.firmware_version_id).first()
        # Return the binary data as a file response
        response = FileResponse(new_firmware.firmware_data, content_type='application/octet-stream', status=210)
        response['Content-Disposition'] = 'attachment; filename="firmware.bin"'
        return response
        

class FirmwareViewSet(viewsets.ModelViewSet):
    queryset = Firmware.objects.all()
    serializer_class = FirmwareSerializer