# /home/ubuntu/platform-services/template_management_service/views.py
# Autor: Szymon Fuchs
# Data: 20.09.2021

from django.http import JsonResponse
from django.views import View
from .models import GraphicTemplate
import json

class TemplateListView(View):
    async def get(self, request, *args, **kwargs):
        templates = GraphicTemplate.objects.filter(is_active=True).values(
            'template_id', 'name', 'description', 'thumbnail_url', 'version', 'tags'
        )
        return JsonResponse(list(templates), safe=False)

# Widok do pobrania szczegółów konkretnego szablonu mógłby być przydatny
class TemplateDetailView(View):
    async def get(self, request, template_id, *args, **kwargs):
        try:
            template = GraphicTemplate.objects.filter(template_id=template_id, is_active=True).values(
                'template_id', 'name', 'description', 'thumbnail_url', 'version', 'tags'
            ).first()
            if template:
                return JsonResponse(template)
            else:
                return JsonResponse({'error': 'Template not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

