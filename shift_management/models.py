from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class Pool(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="The phone number must contain between 9 and 15 digits and can start with '+'."
            )
        ]
    )

    def __str__(self):
        return self.name

class Lifeguard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="The phone number must contain between 9 and 15 digits and can start with '+'."
            )
        ]
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Shift(models.Model):
    pool = models.ForeignKey(Pool, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.pool} on {self.date} {self.start_time}-{self.end_time}"

    def clean(self):
        super().clean()  # Zawsze wywołuj super().clean()
        
        # Sprawdzanie, czy godziny są poprawne
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError({
                'start_time': "Start time must be earlier than end time.",
                'end_time': "End time must be later than start time.",
            })

class Application(models.Model):
    STATUS_CHOICES = [
        ('O', "Pending"),
        ('A', "Accepted"),
        ('R', "Rejected"),
    ]
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    lifeguard = models.ForeignKey(Lifeguard, on_delete=models.CASCADE)
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='O')

    def __str__(self):
        return f"Application {self.lifeguard} for {self.shift}"

class Incident(models.Model):
    INCIDENT_TYPES = [
        ("W", "Rescue action in the water"),
        ("P", "First aid provided"),
        ("A", "Pool malfunction"),
    ]
    pool = models.ForeignKey('Pool', on_delete=models.CASCADE, null=True)
    description = models.TextField()
    date_time = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=1, choices=INCIDENT_TYPES, default="P")
    lifeguard = models.ForeignKey('Lifeguard', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.type} - {self.pool} ({self.date_time})"