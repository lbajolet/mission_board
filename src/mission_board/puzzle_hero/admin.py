from django.contrib import admin

from .models import Submission

class SubmissionAdmin(admin.ModelAdmin):
    pass

admin.site.register(Submission, SubmissionAdmin)

# Register your models here.
