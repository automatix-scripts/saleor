# /home/ubuntu/platform-services/template_management_service/models.py
# Autor: Szymon Fuchs
# Data: 20.09.2021

from django.db import models

class GraphicTemplate(models.Model):
    template_id = models.CharField(max_length=100, unique=True, help_text="Unikalny identyfikator szablonu, np. 'classic_blue'")
    name = models.CharField(max_length=255, help_text="Przyjazna nazwa szablonu")
    description = models.TextField(blank=True, null=True)
    thumbnail_url = models.URLField(blank=True, null=True, help_text="URL do miniaturki podglądu")
    version = models.CharField(max_length=20, default="1.0")
    tags = models.CharField(max_length=255, blank=True, help_text="Tagi oddzielone przecinkami")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.template_id})"
