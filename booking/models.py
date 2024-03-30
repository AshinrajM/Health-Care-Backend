from django.db import models
from accounts.models import Associate


class Available(models.Model):
    associate = models.ForeignKey(Associate, on_delete=models.CASCADE)
    date = models.DateField()
    is_morning = models.BooleanField(default=False)
    is_noon = models.BooleanField(default=False)

    # def __str__(self):
    #     return self.date
