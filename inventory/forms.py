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

    # Server-side validation
    def clean_reason(self):
        reason = self.cleaned_data.get('reason', '').strip()

        if len(reason) < 10:
            raise forms.ValidationError(
                "Reason must be at least 10 characters long."
            )

        if len(reason) > 500:
            raise forms.ValidationError(
                "Reason cannot exceed 500 characters."
            )

        forbidden_strings = [
            "<script",
            "</script>",
            "javascript:"
        ]

        for value in forbidden_strings:
            if value.lower() in reason.lower():
                raise forms.ValidationError(
                    "Invalid characters detected."
                )

        return reason

    def clean_priority(self):
        priority = self.cleaned_data.get('priority')

        if priority not in ['High', 'Medium', 'Low']:
            raise forms.ValidationError(
                "Please select a valid priority."
            )

        return priority


class AdminRequestForm(forms.ModelForm):
    class Meta:
        model = InventoryRequest
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
            }),
        }