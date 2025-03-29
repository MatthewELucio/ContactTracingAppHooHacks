from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Disease(models.Model):
    AIR = 'air'
    PHYSICAL = 'physical'
    DISEASE_TYPE_CHOICES = [
        (AIR, 'Air'),
        (PHYSICAL, 'Physical'),
    ]
    
    name = models.CharField(max_length=100)
    disease_type = models.CharField(
        max_length=20,
        choices=DISEASE_TYPE_CHOICES,
        help_text="Type of disease (air or physical)"
    )

    def __str__(self):
        return self.name
    
# class User(AbstractUser):
#     # Here, each user is linked to an infection record (e.g., their current infection).
#     # If you expect multiple infections per user, consider moving this FK to the Infection model.
#     first_name = models.CharField(max_length=30, blank=True, help_text="User's first name")
#     last_name = models.CharField(max_length=30, blank=True, help_text="User's last name")
#     phone_number = models.CharField(max_length=15, blank=True, help_text="User's phone number")
#     email = models.EmailField(unique=True, help_text="User's email address")
#     date_of_birth = models.DateField(null=True, blank=True, help_text="User's date of birth")
#     address = models.TextField(blank=True, help_text="User's address")
#     is_verified = models.BooleanField(default=False, help_text="Indicates if the user's account is verified")

#     def __str__(self):
#         return f"{self.first_name} {self.last_name} ({self.username})"

class Infection(models.Model):
    # user = models.ForeignKey(
    #     User,
    #     on_delete=models.CASCADE,
    #     related_name='infections',
    #     help_text="The user who is infected"
    # )
    disease = models.ForeignKey(
        Disease,
        on_delete=models.CASCADE,
        related_name='infections',
        help_text="The disease associated with this infection"
    )
    infected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Infection of {self.user.username} with {self.disease.name} at {self.infected_at}"
    
class LocationHistory(models.Model):
    # user = models.ForeignKey(
    #     User,
    #     on_delete=models.CASCADE,
    #     related_name='location_histories'
    # )
    latitude = models.FloatField()
    longitude = models.FloatField()
    # Timestamp to record when the location was saved.
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: ({self.latitude}, {self.longitude}) at {self.recorded_at}"

    # Note: To clear these records every 24 hours, you might use a scheduled task or management command
    # that deletes LocationHistory objects older than 24 hours.


class RelevantLocation(models.Model):
    # user = models.ForeignKey(
    #     User,
    #     on_delete=models.CASCADE,
    #     related_name='relevant_locations'
    # )
    latitude = models.FloatField()
    longitude = models.FloatField()
    # Start and end times representing the period during which the user stayed within a certain radius.
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def duration_minutes(self):
        """Return the duration in minutes that the user spent at this location."""
        delta = self.end_time - self.start_time
        return delta.total_seconds() / 60

    def __str__(self):
        return (f"{self.user.username}: ({self.latitude}, {self.longitude}) "
                f"from {self.start_time} to {self.end_time}")

    # Note: The filtering to determine if a user is within a certain radius for more than 30 minutes
    # should be implemented in your application logic (e.g., as a query or a scheduled process) that
    # examines LocationHistory records and creates RelevantLocation entries accordingly.