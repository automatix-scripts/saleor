# /home/ubuntu/platform-services/account_management_service/models.py                      # Autor: Szymon Fuchs
# Data: 18.08.2021                                                                        
from django.db import models
from django.conf import settings
from django.utils import timezone
import datetime

class EmailChangeRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    new_email = models.EmailField()
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            lifespan_seconds = getattr(settings, 'EMAIL_CHANGE_TOKEN_LIFESPAN_SECONDS', 3600)
            self.expires_at = timezone.now() + datetime.timedelta(seconds=lifespan_seconds)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Email change request for {self.user} to {self.new_email}"

