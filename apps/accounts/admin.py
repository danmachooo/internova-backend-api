from django.contrib import admin

from apps.accounts.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "role", "status", "is_active")
    list_filter = ("role", "status", "is_active")
    search_fields = ("email", "name")
    ordering = ("email",)
