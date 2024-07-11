from django.db import models


# Create your models here.

class Firmware(models.Model):
    version = models.CharField(max_length=10)
    firmware_file = models.FileField(null=True, blank=True)
    firmware_data = models.BinaryField(editable=False)

    def __str__(self):
        return self.version
    
    def save(self, *args, **kwargs):
        if self.firmware_file:
            self.firmware_file.seek(0)
            self.firmware_data = self.firmware_file.read()
            self.firmware_file = None
        super(Firmware, self).save(*args, **kwargs)

class Cards(models.Model):
    rfid = models.CharField(max_length=12, null=True, blank=True, unique=True)

    def __str__(self):
        return self.rfid

class Cars(models.Model):
    mac_address = models.CharField(max_length=17, db_index=True)
    license_plate = models.CharField(max_length=20)    
    firmware_version = models.ForeignKey(Firmware, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.license_plate