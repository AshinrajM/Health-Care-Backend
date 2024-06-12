from django.db import models
from accounts.models import Associate, User
from datetime import date
from django.utils import timezone
from threading import Timer


class Available(models.Model):

    STATUS_CHOICES = [
        ("active", "active"),
        ("booked", "booked"),
        ("asociate_blocked and cancelled", "asociate_blocked and cancelled"),
    ]

    associate = models.ForeignKey(Associate, on_delete=models.CASCADE)
    date = models.DateField()
    is_morning = models.BooleanField(default=False)
    is_noon = models.BooleanField(default=False)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default="active")

    def delete_on_date(self, delay):
        def delete_instance():
            try:
                obj = Available.objects.get(pk=self.pk)
                if obj.date == timezone.now().date() and obj.status != "booked":
                    obj.delete()
                    print(
                        f"Available object with ID {self.pk} has been deleted on {obj.date}."
                    )
                else:
                    if obj.status == "booked":
                        print(
                            f"Available object with ID {self.pk} is booked and cannot be deleted."
                        )
                    else:
                        print(
                            f"Available object with ID {self.pk} is not due for deletion today."
                        )
            except Available.DoesNotExist:
                print(f"Available object with ID {self.pk} does not exist.")

        Timer(delay, delete_instance).start()


class Booking(models.Model):

    STATUS_CHOICES = [
        ("confirmed", "confirmed"),
        ("completed", "completed"),
        ("cancelled", "cancelled"),
        ("cancelled_by_admin", "cancelled_by_admin"),
    ]
    booking_id = models.CharField(max_length=10, default="HC0001", unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slot = models.ForeignKey(Available, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    amount_paid = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    date = models.DateField(default=date(2024, 12, 2))

    status = models.CharField(
        max_length=100,
        choices=STATUS_CHOICES,
        blank=True,
        null=True,
        default="confirmed",
    )
    shift = models.CharField(max_length=20, blank=True, null=True, default="morning")
    created_at = models.DateField(auto_now_add=True)
    location = models.CharField(max_length=200, blank=True, null=True, default="kochi")

    def save(self, *args, **kwargs):
        if (
            not self.pk
        ):  # If the instance is being saved for the first time (i.e., it doesn't have a primary key)
            last_booking = Booking.objects.order_by(
                "-id"
            ).first()  # Retrieve the last booking object based on its ID
            if last_booking:  # If there are existing bookings
                last_id = int(
                    last_booking.booking_id[2:]
                )  # Extract the numerical part of the last booking's ID
                new_id = f"HC{str(last_id + 1).zfill(4)}"  # Increment the numerical part and format it with leading zeros
                self.booking_id = new_id  # Assign the newly generated booking ID to the current instance
        super().save(
            *args, **kwargs
        )  # Call the superclass's save method to actually save the instance


class Rating(models.Model):
    rating_value = models.CharField(max_length=5, blank=True, null=True)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
