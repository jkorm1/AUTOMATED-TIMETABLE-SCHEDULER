from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    email = models.EmailField(_('school email'), unique=True)
    is_student = models.BooleanField(default=False)
    is_lecturer = models.BooleanField(default=False)

    # Keep username, but use email for login if desired
    REQUIRED_FIELDS = ['username']  # username still required
    USERNAME_FIELD = 'email'        # authentication uses email

    def __str__(self):
        return self.email


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    index_number = models.CharField(max_length=20, unique=True)
    program = models.CharField(max_length=100)
    level = models.CharField(max_length=20)
    secondary_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.index_number})"


class LecturerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    staff_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    secondary_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.staff_id})"
