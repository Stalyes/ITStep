from django.contrib import admin

from .models import Course, Lecturer, Student

admin.site.register([Lecturer, Course, Student])
