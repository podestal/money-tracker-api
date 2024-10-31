"""
Tracker admin customization.
"""

from django.contrib import admin
from . import models

admin.site.register(models.Balance)
admin.site.register(models.Transaction)
admin.site.register(models.Category)
admin.site.register(models.Project)
admin.site.register(models.Task)
admin.site.register(models.Team)
