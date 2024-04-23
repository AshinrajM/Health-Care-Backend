from django.db import models
from accounts.models import Associate, User


class Available(models.Model):
    associate = models.ForeignKey(Associate, on_delete=models.CASCADE)
    date = models.DateField()
    is_morning = models.BooleanField(default=False)
    is_noon = models.BooleanField(default=False)


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slot = models.ForeignKey(Available, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    amount_paid = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    status = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)
