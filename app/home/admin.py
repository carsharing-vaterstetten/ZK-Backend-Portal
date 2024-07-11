from django.contrib import admin
from .models import Cards, Firmware, Cars, Logs
from .forms import FirmwareAdminForm
from django.utils import timezone

admin.site.site_header = 'Zugangskontrolle Administration'
admin.site.site_title = 'ZK Administration'
admin.site.index_title = 'Administration'

class CarsAdmin(admin.ModelAdmin):
    list_display = ('mac_address', 'license_plate', 'firmware_version')
    list_filter = ('firmware_version',)
    search_fields = ('mac_address', 'license_plate')
    
class FirmwareAdmin(admin.ModelAdmin):
    form = FirmwareAdminForm
    list_display = ['version', 'firmware_file']

class LogsAdmin(admin.ModelAdmin):
    list_display = ('uploaded_at_view', 'uploaded_by', 'license_plate', 'created_at_view', 'firmware_version', 'log')
    list_filter = ('uploaded_by', 'firmware_version')
    search_fields = ('uploaded_by', 'log', 'firmware_version')
    ordering = ('-uploaded_at',)
    readonly_fields = ('uploaded_at', 'uploaded_by', 'license_plate', 'created_at', 'firmware_version', 'log')

    def uploaded_at_view(self, obj):
        return obj.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
    uploaded_at_view.short_description = 'Log wurde hochgeladen am'

    def created_at_view(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
    created_at_view.short_description = 'Log wurde erstellt am'

    def license_plate(self, obj):
        try:
            car = Cars.objects.get(mac_address=obj.uploaded_by)
            return car.license_plate
        except Cars.DoesNotExist:
            return 'Unknown'
    license_plate.short_description = 'Autokennzeichen'

admin.site.register(Cars, CarsAdmin)
admin.site.register(Logs, LogsAdmin)    
admin.site.register(Firmware, FirmwareAdmin)
admin.site.register(Cards)