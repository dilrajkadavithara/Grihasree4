import uuid
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.utils.text import slugify  # <-- REQUIRED for auto-slug
from smart_selects.db_fields import ChainedForeignKey

# === Custom Manager to return only active records ===
class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

# === Abstract base class for reusable fields ===
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Updated")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

# === District Model ===
class District(TimeStampedModel):
    district_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    district_name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="District Name",
        help_text="Enter the name of the district."
    )
    slug = models.SlugField(unique=True, blank=True, help_text="URL-friendly identifier for the district.")

    def __str__(self):
        return self.district_name

    class Meta:
        verbose_name_plural = "Districts"

    def save(self, *args, **kwargs):
        if not self.slug and self.district_name:
            self.slug = slugify(self.district_name)
        super().save(*args, **kwargs)

# === Location Model ===
class Location(TimeStampedModel):
    location_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    location_name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Location Name",
        help_text="Enter the name of the location/area."
    )
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        related_name="locations",
        verbose_name="District"
    )
    slug = models.SlugField(unique=True, blank=True, help_text="URL-friendly identifier for the location.")

    def __str__(self):
        return f"{self.location_name} ({self.district.district_name})"

    def save(self, *args, **kwargs):
        if not self.slug and self.location_name:
            self.slug = slugify(self.location_name)
        super().save(*args, **kwargs)

# === Service Model ===
class Service(TimeStampedModel):
    service_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service_name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Service Name",
        help_text="Enter the name of the service offered."
    )
    slug = models.SlugField(unique=True, blank=True, help_text="URL-friendly identifier for the service.")

    def __str__(self):
        return self.service_name

    class Meta:
        verbose_name_plural = "Services"

    def save(self, *args, **kwargs):
        if not self.slug and self.service_name:
            self.slug = slugify(self.service_name)
        super().save(*args, **kwargs)

# === Vendor Model (Chained Location for now) ===
class Vendor(TimeStampedModel):
    vendor_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor_name = models.CharField(max_length=100, verbose_name="Vendor Name")
    phone_number = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex=r'^\d{10}$', message="Phone number must be exactly 10 digits")],
        blank=True,
        null=True,
        verbose_name="Phone Number",
        help_text="Enter a valid 10-digit phone number."
    )
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="vendors")
    location = ChainedForeignKey(
        Location,
        chained_field="district",
        chained_model_field="district",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.CASCADE,
        related_name="vendor_locations",
        verbose_name="Location"
    )

    def __str__(self):
        return f"{self.vendor_name} ({self.location.location_name})"

# === Lead Model (NO chained foreign key, ready for AJAX) ===
class Lead(TimeStampedModel):
    lead_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead_name = models.CharField(
        max_length=100,
        verbose_name="Lead Name",
        help_text="Enter the full name of the customer."
    )
    phone_number = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex=r'^\d{10}$', message="Phone number must be exactly 10 digits")],
        db_index=True,
        verbose_name="Phone Number",
        help_text="Enter a valid 10-digit phone number."
    )
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        related_name="leads",
        verbose_name="District"
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="leads",
        verbose_name="Location"
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="leads",
        verbose_name="Service Requested"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_leads",
        verbose_name="Created By"
    )

    def __str__(self):
        try:
            district_name = self.district.district_name if self.district else "N/A"
        except Exception:
            district_name = "N/A"
        try:
            location_name = self.location.location_name if self.location else "N/A"
        except Exception:
            location_name = "N/A"
        try:
            service_name = self.service.service_name if self.service else "N/A"
        except Exception:
            service_name = "N/A"
        return (
            f"Lead ID: {self.lead_id} | "
            f"Name: {self.lead_name} | "
            f"Phone: {self.phone_number} | "
            f"District: {district_name} | "
            f"Location: {location_name} | "
            f"Service: {service_name}"
        )
