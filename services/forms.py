from django import forms
from .models import Lead, Vendor, District, Location, Service
from django.core.validators import RegexValidator
from django.utils.text import slugify
from django.contrib.auth.models import User

# --- LeadForm ---
class LeadForm(forms.ModelForm):
    phone_number = forms.CharField(
        max_length=10,
        required=True,
        label="Phone Number",
        validators=[RegexValidator(regex=r'^[6-9]\d{9}$', message="Enter a valid 10-digit Indian mobile number")],
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. 9876543210',
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200',
            'id': 'phone-input'
        })
    )

    district = forms.ModelChoiceField(
        queryset=District.objects.filter(is_active=True),
        required=True,
        label="Select District",
        widget=forms.Select(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200',
            'id': 'district-select'
        })
    )

    location = forms.ModelChoiceField(
        queryset=Location.objects.none(),
        required=True,
        label="Select Local Area",
        widget=forms.Select(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200',
            'id': 'location-select',
            'disabled': 'disabled'
        })
    )

    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_active=True),
        required=True,
        label="Type of Service Required",
        widget=forms.Select(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200',
            'id': 'service-select'
        })
    )

    class Meta:
        model = Lead
        fields = ['lead_name', 'phone_number', 'district', 'location', 'service']
        widgets = {
            'lead_name': forms.TextInput(attrs={
                'placeholder': 'Your Full Name',
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200',
                'id': 'name-input'
            }),
        }
        labels = {
            'lead_name': 'Full Name',
            'district': 'Select District',
            'location': 'Select Local Area',
            'service': 'Type of Service Required'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'district' in self.data:
            try:
                district_id = self.data.get('district')
                self.fields['location'].queryset = Location.objects.filter(district_id=district_id, is_active=True)
                self.fields['location'].widget.attrs.pop('disabled', None)
            except (ValueError, TypeError):
                self.fields['location'].queryset = Location.objects.none()
        elif self.instance.pk and getattr(self.instance, "district_id", None):
            self.fields['location'].queryset = Location.objects.filter(district=self.instance.district, is_active=True)
            self.fields['location'].widget.attrs.pop('disabled', None)
        else:
            self.fields['location'].queryset = Location.objects.none()
            self.fields['location'].widget.attrs['disabled'] = 'disabled'

    # NEW: Ensure selected location belongs to the selected district
    def clean(self):
        cleaned_data = super().clean()
        district = cleaned_data.get('district')
        location = cleaned_data.get('location')
        if district and location and location.district != district:
            self.add_error('location', "Selected location does not belong to the selected district.")
        return cleaned_data

# --- VendorForm ---
class VendorForm(forms.ModelForm):
    phone_number = forms.CharField(
        max_length=10,
        required=False,
        label="Phone Number",
        validators=[RegexValidator(regex=r'^[6-9]\d{9}$', message="Enter a valid 10-digit Indian mobile number")],
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. 9876543210',
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200',
            'id': 'vendor-phone-input'
        })
    )

    district = forms.ModelChoiceField(
        queryset=District.objects.filter(is_active=True),
        required=True,
        label="District",
        widget=forms.Select(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200',
            'id': 'vendor-district-select'
        })
    )

    location = forms.ModelChoiceField(
        queryset=Location.objects.none(),
        required=True,
        label="Local Area",
        widget=forms.Select(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200',
            'id': 'vendor-location-select',
            'disabled': 'disabled'
        })
    )

    class Meta:
        model = Vendor
        fields = ['vendor_name', 'phone_number', 'district', 'location']
        widgets = {
            'vendor_name': forms.TextInput(attrs={
                'placeholder': 'Enter vendor name',
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200',
                'id': 'vendor-name-input'
            }),
        }
        labels = {
            'vendor_name': 'Vendor Name',
            'phone_number': 'Phone Number',
            'district': 'District',
            'location': 'Local Area',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'district' in self.data:
            try:
                district_id = self.data.get('district')
                self.fields['location'].queryset = Location.objects.filter(district_id=district_id, is_active=True)
                self.fields['location'].widget.attrs.pop('disabled', None)
            except (ValueError, TypeError):
                self.fields['location'].queryset = Location.objects.none()
        elif self.instance.pk and getattr(self.instance, "district_id", None):
            self.fields['location'].queryset = Location.objects.filter(district=self.instance.district, is_active=True)
            self.fields['location'].widget.attrs.pop('disabled', None)
        else:
            self.fields['location'].queryset = Location.objects.none()
            self.fields['location'].widget.attrs['disabled'] = 'disabled'

# --- LocationForm ---
class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['location_name', 'district']
        widgets = {
            'location_name': forms.TextInput(attrs={
                'placeholder': 'Enter location name',
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200',
                'id': 'location-name-input'
            }),
            'district': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200',
                'id': 'location-district-select'
            }),
        }
        labels = {
            'location_name': 'Location Name',
            'district': 'District',
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = slugify(instance.location_name)
        if commit:
            instance.save()
        return instance

# --- DistrictForm ---
class DistrictForm(forms.ModelForm):
    class Meta:
        model = District
        fields = ['district_name']
        widgets = {
            'district_name': forms.TextInput(attrs={
                'placeholder': 'Enter district name',
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200',
                'id': 'district-name-input'
            }),
        }
        labels = {
            'district_name': 'District Name',
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = slugify(instance.district_name)
        if commit:
            instance.save()
        return instance

# --- ServiceForm ---
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['service_name']
        widgets = {
            'service_name': forms.TextInput(attrs={
                'placeholder': 'Enter service name (e.g. Plumbing, Electrical)',
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200',
                'id': 'service-name-input'
            }),
        }
        labels = {
            'service_name': 'Service Name',
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = slugify(instance.service_name)
        if commit:
            instance.save()
        return instance

# --- RegisterForm ---
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200',
        'placeholder': 'Enter password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200',
        'placeholder': 'Confirm password'
    }))

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Enter your username',
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter your email',
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
