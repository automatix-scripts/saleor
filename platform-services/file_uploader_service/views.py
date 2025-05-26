# /home/ubuntu/platform-services/file_uploader_service/views.py
# Autor: Szymon Fuchs
# Data: 20.08.2021

from django.http import JsonResponse
from django.views import View
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import uuid

class CompanyGalleryUploadView(View):
    async def post(self, request, *args, **kwargs):
        if not request.FILES.get('image'):
            return JsonResponse({'error': 'No image provided'}, status=400)

        image = request.FILES['image']
        
        allowed_extensions = ['.jpg', '.jpeg', '.png']
        ext = os.path.splitext(image.name)[1].lower()
        if ext not in allowed_extensions:
            return JsonResponse({'error': 'Invalid file type. Allowed: JPG, PNG.'}, status=400)
        
        if image.size > 5 * 1024 * 1024: 
             return JsonResponse({'error': 'Image size exceeds 5MB limit.'}, status=400)

        user_company_id_placeholder = "user_or_company_id_123" 
        
        fs_path = os.path.join(settings.MEDIA_ROOT, 'company_galleries', user_company_id_placeholder)
        # Upewnij się, że katalog istnieje
        os.makedirs(fs_path, exist_ok=True)

        fs = FileSystemStorage(location=fs_path, base_url=os.path.join(settings.MEDIA_URL, 'company_galleries', user_company_id_placeholder))
        
        filename = fs.save(f"{uuid.uuid4()}{ext}", image)
        file_url = fs.url(filename)

        return JsonResponse({'message': 'Image uploaded successfully', 'url': file_url})
