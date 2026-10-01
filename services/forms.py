"""
Forms for the Services app (admin service management).
"""
from django import forms
from .models import Service, ServiceCategory


class ServiceForm(forms.ModelForm):
    """Form for admin to add/edit services."""
    class Meta:
        model = Service
        fields = [
            'name', 'category', 'slug', 'description', 'short_description',
            'price', 'duration_minutes', 'image', 'is_active', 'is_featured', 'display_order',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'slug': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'short_description': forms.TextInput(attrs={'class': 'form-input'}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-input'}),
        }


class ServiceCategoryForm(forms.ModelForm):
    """Form for admin to add/edit service categories."""
    class Meta:
        model = ServiceCategory
        fields = ['name', 'slug', 'description', 'icon', 'display_order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'slug': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. ✂️ or 💆'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-input'}),
        }
