from django.contrib import admin
from users.models import User, Profile
# Register your models here.


class ProfileInLine(admin.TabularInline):
    model = Profile
    fields = ('profile_picture_preview', 'ID_card_preview')
    readonly_fields = ('profile_picture_preview', 'ID_card_preview')
    extra = False
    max_num = 1


class UserAdmin(admin.ModelAdmin):
    inlines = [ProfileInLine]
    exclude = ('password',)
    readonly_fields = ('date_joined', 'last_login')
    list_display = ('username', 'email', 'phone_number', 'is_active', 'is_staff', 'is_superuser', 'last_login')
    list_editable = ('is_active', 'is_staff', 'is_superuser')


admin.site.register(User, UserAdmin)
admin.site.register(Profile)
