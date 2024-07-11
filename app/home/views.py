from django.http import FileResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView, RetrieveAPIView
from rest_framework.mixins import UpdateModelMixin, CreateModelMixin
from rest_framework.permissions import IsAdminUser
from .serializer import CardSerializer, CarsSerializer, FirmwareSerializer, LogSerializer
from .models import Cards, Cars, Firmware, Logs
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from django.utils.dateparse import parse_datetime
from datetime import datetime

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
    permission_classes = (IsAdminUser, )
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
        response['Content-Length'] = len(new_firmware.firmware_data)
        return response
        

class FirmwareViewSet(viewsets.ModelViewSet):
    queryset = Firmware.objects.all()
    serializer_class = FirmwareSerializer

class ReceiveLogsView(APIView):
    permission_classes = (IsAdminUser, )
    def post(self, request, format=None):
        data = request.data
        mac_address = data.get('mac_address')
        logs = data.get('logs', [])

        if not mac_address or not logs:
            return Response(
                {'error': 'mac_address and logs are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        for log_entry in logs:
            created_at_str = log_entry.get('created_at')
            firmware_version = log_entry.get('firmware_version')
            log_text = log_entry.get('log')

            if not all([created_at_str, firmware_version, log_text]):
                return Response(
                    {'error': 'Each log entry must contain created_at, firmware_version, and log.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            created_at = None
            try:
                created_at = parse_datetime(created_at_str)
                if created_at is None: 
                    if '+' in created_at_str:
                        created_at_str = created_at_str.split('+')[0]
                        created_at = datetime.strptime(created_at_str, "%y/%m/%d,%H:%M:%S")  
            except (ValueError, TypeError):
                # Wenn Arduino falsches Datum schickt schreiebn wir einfach 1970-01-01 00:00:00.
                # m.E. macht es keinen sinn hierfür eine Fehlermeldung zu schicken
                created_at = datetime(1970, 1, 1)

            log_data = {
                'uploaded_by': mac_address,
                'created_at': created_at,
                'firmware_version': firmware_version,
                'log': log_text
            }

            serializer = LogSerializer(data=log_data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'status': 'success'}, status=status.HTTP_201_CREATED)    