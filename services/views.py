from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User, Group

from .models import Lead, Vendor, Location, District, Service
from .forms import LeadForm, VendorForm, LocationForm, DistrictForm, ServiceForm, RegisterForm

# === AJAX VIEW for Dependent Dropdowns ===

def load_locations(request):
    district_id = request.GET.get('district_id')
    locations = Location.objects.filter(district_id=district_id, is_active=True).order_by('location_name')
    data = [{'id': loc.pk, 'name': loc.location_name} for loc in locations]
    return JsonResponse({'locations': data})

# === Role Checkers ===

def is_it_head(user):
    return user.groups.filter(name='IT Head').exists()

def is_director(user):
    return user.groups.filter(name='Directors').exists()

def is_rm(user):
    return user.groups.filter(name='RM').exists()

def is_director_or_ithead(user):
    return user.is_superuser or is_it_head(user) or is_director(user)

# === Public Views ===

def home(request):
    if request.method == 'POST':
        if 'desktop-submit' in request.POST:
            form = LeadForm(request.POST, prefix='desktop')
            mobile_form = LeadForm(prefix='mobile')
            district_id = request.POST.get('desktop-district')
            if district_id:
                form.fields['location'].queryset = Location.objects.filter(district_id=district_id)
            else:
                form.fields['location'].queryset = Location.objects.none()
        else:
            form = LeadForm(prefix='desktop')
            mobile_form = LeadForm(request.POST, prefix='mobile')
            district_id = request.POST.get('mobile-district')
            if district_id:
                mobile_form.fields['location'].queryset = Location.objects.filter(district_id=district_id)
            else:
                mobile_form.fields['location'].queryset = Location.objects.none()

        # Validate and process the right form
        if (('desktop-submit' in request.POST and form.is_valid()) or
            ('mobile-submit' in request.POST and mobile_form.is_valid())):
            (form if 'desktop-submit' in request.POST else mobile_form).save()
            return redirect('success')
    else:
        form = LeadForm(prefix='desktop')
        mobile_form = LeadForm(prefix='mobile')

    context = {
        'form': form,
        'mobile_form': mobile_form
    }
    return render(request, 'services/home.html', context)

# === Dashboard Redirect ===

@login_required
def redirect_dashboard_view(request):
    user = request.user
    if is_it_head(user):
        return redirect("it_dashboard")
    elif is_director(user):
        return redirect("director_dashboard")
    elif is_rm(user):
        return redirect("rm_dashboard")
    return redirect("home")

# === Dashboards ===

@login_required
@user_passes_test(is_it_head)
def it_dashboard_view(request):
    return render(request, 'services/it_dashboard.html')

@login_required
@user_passes_test(is_director)
def director_dashboard_view(request):
    return render(request, 'services/director_dashboard.html')

@login_required
@user_passes_test(is_rm)
def rm_dashboard_view(request):
    return render(request, 'services/rm_dashboard.html')

# === Leads (IT Head, Director, RM) ===

@login_required
def leads_view(request):
    leads = Lead.all_objects.select_related("district", "location", "service").order_by("-created_at")
    return render(request, "services/leads.html", {"leads": leads})

@login_required
def create_lead_view(request):
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.created_by = request.user
            lead.save()
            messages.success(request, "Lead created successfully!")
            return redirect('leads_view')
    else:
        form = LeadForm()
    return render(request, 'services/lead_form.html', {'form': form, 'action': 'Create'})

@login_required
def edit_lead_view(request, lead_id):
    lead = get_object_or_404(Lead, pk=lead_id)
    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            messages.success(request, "Lead updated successfully!")
            return redirect('leads_view')
    else:
        form = LeadForm(instance=lead)
    return render(request, 'services/lead_form.html', {'form': form, 'action': 'Update'})

@login_required
def delete_lead_view(request, lead_id):
    lead = get_object_or_404(Lead, pk=lead_id)
    if request.method == 'POST':
        lead.delete()
        messages.success(request, "Lead deleted successfully.")
        return redirect('leads_view')
    return render(request, 'services/lead_confirm_delete.html', {'lead': lead})

# === Vendors (IT Head, Director, RM) ===

@login_required
def vendors_view(request):
    vendors = Vendor.all_objects.select_related("district", "location").order_by("vendor_name")
    return render(request, "services/vendors.html", {"vendors": vendors})

@login_required
@user_passes_test(is_director_or_ithead)
def create_vendor_view(request):
    if request.method == 'POST':
        form = VendorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Vendor added successfully!")
            return redirect('vendors_view')
    else:
        form = VendorForm()
    return render(request, 'services/vendor_form.html', {'form': form, 'action': 'Create'})

@login_required
@user_passes_test(is_director_or_ithead)
def edit_vendor_view(request, vendor_id):
    vendor = get_object_or_404(Vendor, pk=vendor_id)
    if request.method == 'POST':
        form = VendorForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            messages.success(request, "Vendor updated successfully!")
            return redirect('vendors_view')
    else:
        form = VendorForm(instance=vendor)
    return render(request, 'services/vendor_form.html', {'form': form, 'action': 'Update'})

@login_required
@user_passes_test(is_director_or_ithead)
def delete_vendor_view(request, vendor_id):
    vendor = get_object_or_404(Vendor, pk=vendor_id)
    if request.method == 'POST':
        vendor.delete()
        messages.success(request, "Vendor deleted successfully.")
        return redirect('vendors_view')
    return render(request, 'services/vendor_confirm_delete.html', {'vendor': vendor})

# === Location Views (IT Head, Director) ===

@login_required
@user_passes_test(is_director_or_ithead)
def locations_view(request):
    locations = Location.all_objects.select_related("district").order_by("district__district_name", "location_name")
    return render(request, "services/locations.html", {"locations": locations})

@login_required
@user_passes_test(is_director_or_ithead)
def create_location_view(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Location added successfully!")
            return redirect('locations_view')
    else:
        form = LocationForm()
    return render(request, 'services/location_form.html', {'form': form, 'action': 'Create'})

@login_required
@user_passes_test(is_director_or_ithead)
def edit_location_view(request, location_id):
    location = get_object_or_404(Location, pk=location_id)
    if request.method == 'POST':
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            messages.success(request, "Location updated successfully!")
            return redirect('locations_view')
    else:
        form = LocationForm(instance=location)
    return render(request, 'services/location_form.html', {'form': form, 'action': 'Update'})

@login_required
@user_passes_test(is_director_or_ithead)
def delete_location_view(request, location_id):
    location = get_object_or_404(Location, pk=location_id)
    if request.method == 'POST':
        location.delete()
        messages.success(request, "Location deleted successfully.")
        return redirect('locations_view')
    return render(request, 'services/location_confirm_delete.html', {'location': location})

# === District Views (IT Head, Director) ===

@login_required
@user_passes_test(is_director_or_ithead)
def districts_view(request):
    districts = District.all_objects.all().order_by("district_name")
    return render(request, "services/districts.html", {"districts": districts})

@login_required
@user_passes_test(is_director_or_ithead)
def create_district_view(request):
    if request.method == 'POST':
        form = DistrictForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "District created successfully.")
            return redirect('districts_view')
    else:
        form = DistrictForm()
    return render(request, 'services/district_form.html', {'form': form, 'action': 'Create'})

@login_required
@user_passes_test(is_director_or_ithead)
def edit_district_view(request, district_id):
    district = get_object_or_404(District, pk=district_id)
    if request.method == 'POST':
        form = DistrictForm(request.POST, instance=district)
        if form.is_valid():
            form.save()
            messages.success(request, "District updated successfully.")
            return redirect('districts_view')
    else:
        form = DistrictForm(instance=district)
    return render(request, 'services/district_form.html', {'form': form, 'action': 'Update'})

@login_required
@user_passes_test(is_director_or_ithead)
def delete_district_view(request, district_id):
    district = get_object_or_404(District, pk=district_id)
    if request.method == 'POST':
        district.delete()
        messages.success(request, "District deleted successfully.")
        return redirect('districts_view')
    return render(request, 'services/district_confirm_delete.html', {'district': district})

# === Service Views (IT Head, Director) ===

@login_required
@user_passes_test(is_director_or_ithead)
def services_view(request):
    services = Service.all_objects.all().order_by("service_name")
    return render(request, "services/services.html", {"services": services})

@login_required
@user_passes_test(is_director_or_ithead)
def create_service_view(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Service created successfully.")
            return redirect('services_view')
    else:
        form = ServiceForm()
    return render(request, 'services/service_form.html', {'form': form, 'action': 'Create'})

@login_required
@user_passes_test(is_director_or_ithead)
def edit_service_view(request, service_id):
    service = get_object_or_404(Service, pk=service_id)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Service updated successfully.")
            return redirect('services_view')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'services/service_form.html', {'form': form, 'action': 'Update'})

@login_required
@user_passes_test(is_director_or_ithead)
def delete_service_view(request, service_id):
    service = get_object_or_404(Service, pk=service_id)
    if request.method == 'POST':
        service.delete()
        messages.success(request, "Service deleted successfully.")
        return redirect('services_view')
    return render(request, 'services/service_confirm_delete.html', {'service': service})

# === User Registration and Approval ===

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            messages.success(request, "Your registration is pending approval. You will be notified once your account is activated.")
            return redirect('registration_feedback')
        else:
            messages.error(request, "There was an error with your submission. Please check the form.")
            return render(request, 'services/register.html', {'form': form})
    else:
        form = RegisterForm()
    return render(request, 'services/register.html', {'form': form})

def pending_users_view(request):
    pending_users = User.objects.filter(is_active=False)
    return render(request, 'services/pending_users.html', {'users': pending_users})

def success_view(request):
    return render(request, 'services/success.html')

@login_required
@user_passes_test(is_director_or_ithead)
def approve_user_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if not user.is_active:
        user.is_active = True
        user.save()
        messages.success(request, f"User '{user.username}' has been approved.")
    else:
        messages.info(request, f"User '{user.username}' is already active.")
    return redirect('pending_users')

@login_required
@user_passes_test(is_director_or_ithead)
def assign_group_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        group_ids = request.POST.getlist('groups')
        user.groups.clear()
        for group_id in group_ids:
            try:
                group = Group.objects.get(id=group_id)
                user.groups.add(group)
            except Group.DoesNotExist:
                messages.error(request, f"Group with ID {group_id} does not exist.")
        messages.success(request, f"Groups assigned to user '{user.username}' successfully.")
        return redirect('pending_users')
    else:
        groups = Group.objects.all()
        return render(request, 'services/assign_group.html', {'user': user, 'groups': groups})

def registration_feedback_view(request):
    return render(request, 'services/registration_feedback.html')
