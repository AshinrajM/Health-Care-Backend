from django.db import models
from accounts.models import User

# Create your models here.


class Chat(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="send_message"
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="receive_message"
    )
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.sender} - {self.receiver}"
