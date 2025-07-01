from django import forms
from .models import InventoryRequest


class RequestForm(forms.ModelForm):
    class Meta:
        model = InventoryRequest
        fields = ['item', 'reason', 'priority']
        widgets = {
            'item': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your reason for the request',
                'required': 'required',
                'rows': 3,
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True


class AdminRequestForm(forms.ModelForm):
    class Meta:
        model = InventoryRequest
        fields = ['status']  # Admins can update only the status
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
            }),
        }
