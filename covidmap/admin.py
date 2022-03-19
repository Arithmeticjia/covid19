from django.contrib import admin

# Register your models here.
from covidmap import models

admin.site.register(models.Location)
admin.site.register(models.CovidHistory)
admin.site.register(models.CovidCurrent)
