from django.db import models


class Lecturer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Course(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    credits = models.PositiveIntegerField(default=3)
    lecturer = models.ForeignKey(
        Lecturer,
        on_delete=models.CASCADE,
        related_name="courses",
    )

    def __str__(self):
        return self.title


class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    enrollment_date = models.DateField(auto_now_add=True)
    courses = models.ManyToManyField(Course, related_name="students", blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
