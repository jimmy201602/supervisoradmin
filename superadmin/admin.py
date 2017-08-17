from django.contrib import admin
from superadmin.models import NodeEnv,EnvironmentGroups,Log
class EnvironmentGroupsDisplay(admin.ModelAdmin):
    filter_horizontal = ('members',)  
admin.site.register(NodeEnv)
admin.site.register(EnvironmentGroups,EnvironmentGroupsDisplay)
admin.site.register(Log)