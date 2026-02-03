from django.contrib import admin
from .models import HomeSettings, Feature

@admin.register(HomeSettings)
class HomeSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Allow adding provided no instance exists
        if  HomeSettings.objects.exists():
            return False
        return True

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ['title', 'icon', 'order']
    list_editable = ['order']
