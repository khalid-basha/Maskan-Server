from django.contrib import admin
from properties.models import *
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.forms.widgets import OSMWidget


class LocationAdmin(admin.ModelAdmin):
    formfield_overrides = {
        gis_models.PointField: {'widget': OSMWidget},
    }


# Register your models here.
class ApartmentInLine(admin.TabularInline):
    model = Apartment
    extra = 0
    can_delete = False


class HouseInLine(admin.TabularInline):
    model = House
    extra = 0
    can_delete = False


class ImageInLine(admin.StackedInline):
    model = Image
    readonly_fields = ['image_preview', 'image']
    extra = False
    can_delete = True


class FeaturesInLine(admin.StackedInline):
    model = Features
    fields = ('features',)
    readonly_fields = ('features',)
    can_delete = False


class LocationInLine(admin.TabularInline):
    model = Location


class OwnershipInLine(admin.StackedInline):
    model = Ownership
    exclude = ('record',)
    readonly_fields = ('record_preview', 'is_viewable')
    can_delete = False


class HomeAdmin(admin.ModelAdmin):
    # fields = '__all__'
    list_display = ('id', 'owner', 'price', 'type', 'state', 'is_pending')
    list_editable = ('is_pending',)
    list_filter = ('price', 'is_pending', 'owner', 'views')
    radio_fields = {"state": admin.VERTICAL, "type": admin.VERTICAL}
    inlines = [ApartmentInLine, HouseInLine, OwnershipInLine,
               ImageInLine, FeaturesInLine]
    readonly_fields = ('visited_by',)

    def make_posted(self, request, queryset):
        queryset.update(is_pending=False)

    make_posted.short_description = "Post selected homes"

    def make_pending(self, request, queryset):
        queryset.update(is_pending=True)

    actions = [make_posted, make_pending]
    make_pending.short_description = "Pend selected homes"

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        if not is_superuser:
            form.base_fields['price'].disabled = True
            form.base_fields['area'].disabled = True
            form.base_fields['description'].disabled = True
            form.base_fields['built_year'].disabled = True
            form.base_fields['type'].disabled = True
            form.base_fields['state'].disabled = True
            form.base_fields['owner'].disabled = True
        return form


admin.site.register(Home, HomeAdmin)
admin.site.register(House)
admin.site.register(Apartment)
admin.site.register(Location, LocationAdmin)
admin.site.register(LivingSpace)
admin.site.register(Features)
admin.site.register(Image)
admin.site.register(Ownership)
