from django import forms
from .models import CSVFile

class CSVFileForm(forms.ModelForm):
    """Form For Uploading CSV File"""
    class Meta:
        model = CSVFile
        fields = ['file']
