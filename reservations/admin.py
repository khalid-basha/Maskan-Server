from django.contrib import admin
from reservations.models import TimeSlot


# Register your models here.
class TimeSlotAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    empty_value_display = "-empty-"
    fields = [
        'id',
        'date',
        'user',
        'home',
        'reserved_by',
        ('start_time',
         'end_time')]
    readonly_fields = (
        'id',
        'user',
        'start_time',
        'end_time')
    list_display = (
        'id',
        'title',
        'reserved_by',
        'home',
        'date',
        'start_time')
    list_per_page = 15
    list_filter = ('date', 'reserved_by')
    ordering = ('date', 'start_time', 'user', 'reserved_by')
    list_display_links = ('title', 'id')
    list_select_related = ['home']
    search_fields = ["reserved_by__username", 'home__owner__username', 'home__id']

    @admin.display(empty_value="UNKNOWN")
    def title(self, obj):
        return "{}, date:{}, start at:{}".format(obj.user, obj.date, obj.start_time)


admin.site.register(TimeSlot, TimeSlotAdmin)
