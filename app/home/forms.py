from django import forms
from .models import Firmware


class FirmwareAdminForm(forms.ModelForm):
    firmware_file = forms.FileField(required=False)
    class Meta:
        model = Firmware
        fields = '__all__'

    def save(self, commit=True):
        instance = super(FirmwareAdminForm, self).save(commit=False)
        if self.cleaned_data.get('firmware_file'):
            instance.firmware_file = self.cleaned_data['firmware_file']
        if commit:
            instance.save()
        return instance