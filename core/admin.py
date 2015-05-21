from django.contrib import admin
from core.models import Project, Skills, Skills_categories, UserProfile, Collaboration

# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Project)
admin.site.register(Skills)
admin.site.register(Skills_categories)
admin.site.register(Collaboration)
