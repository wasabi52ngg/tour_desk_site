from django.contrib import admin
from .models import Review, Booking, Tour, Location, Guide, Category, LocationPhoto, TourSession


# Register your models here.
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    exclude = ['slug', 'created_at']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    exclude = ['created_at', 'updated_at', 'slug']
    readonly_fields = ['total_price']


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    readonly_fields = ['slug']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    readonly_fields = ['slug']


@admin.register(Guide)
class GuideAdmin(admin.ModelAdmin):
    readonly_fields = ['slug']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    readonly_fields = ['slug']

@admin.register(LocationPhoto)
class LocationPhotoAdmin(admin.ModelAdmin):
    fields = ['location','photo']


@admin.register(TourSession)
class TourSessionAdmin(admin.ModelAdmin):
    pass