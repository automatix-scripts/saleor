# /home/ubuntu/platform-services/monitoring_service/views.py
# Autor: Szymon Fuchs
# Data: 05.10.2021

from django.http import JsonResponse
from django.views import View
from django.db import connection
from django.apps import apps 

class HealthCheckView(View):
    async def get(self, request, *args, **kwargs):
        db_ok = False
        db_error_message = "OK"
        celery_ok = False 
        celery_error_message = "Not checked" 

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                if cursor.fetchone()[0] != 1:
                    raise Exception("DB returned unexpected value")
            db_ok = True
        except Exception as e:
            db_error_message = str(e)
            db_ok = False
        
        celery_ok = True 

        if db_ok and celery_ok:
            return JsonResponse({'status': 'ok', 'database': 'ok', 'celery_broker': 'ok'})
        else:
            details = {}
            if not db_ok: details['database'] = db_error_message
            if not celery_ok: details['celery_broker'] = celery_error_message
            return JsonResponse({'status': 'error', 'details': details}, status=503)

class ResourceMetricsDataView(View):
    async def get(self, request, resource_id, *args, **kwargs):
        MonitoredResource = apps.get_model('monitoring_service', 'MonitoredResource')
        ResourceMetricLog = apps.get_model('monitoring_service', 'ResourceMetricLog')
        try:
            resource = MonitoredResource.objects.get(id=resource_id)
        except MonitoredResource.DoesNotExist:
            return JsonResponse({'error': 'Resource not found'}, status=404)

        limit = int(request.GET.get('limit', 100))
        metric_name = request.GET.get('metric_name')
        
        query = ResourceMetricLog.objects.filter(resource=resource).select_related('metric_definition')
        if metric_name:
            query = query.filter(metric_definition__name=metric_name)
        
        metrics_log = query.order_by('-timestamp')[:limit]
        
        data = [{
            'timestamp': log.timestamp.isoformat(),
            'metric_name': log.metric_definition.name,
            'value': log.value,
            'unit': log.metric_definition.unit
        } for log in metrics_log]
        
        return JsonResponse({'resource_name': resource.name, 'metrics': data})

class RecentAlertsView(View):
    async def get(self, request, *args, **kwargs):
        AlertLog = apps.get_model('monitoring_service', 'AlertLog')
        limit = int(request.GET.get('limit', 50))
        resource_id = request.GET.get('resource_id')

        query = AlertLog.objects.all().select_related('resource', 'threshold', 'threshold__metric_definition')
        if resource_id:
            try:
                resource_id_int = int(resource_id)
                query = query.filter(resource_id=resource_id_int)
            except ValueError:
                return JsonResponse({'error': 'Invalid resource_id format'}, status=400)

        alerts = query.order_by('-timestamp')[:limit]
        
        data = [{
            'id': alert.id,
            'timestamp': alert.timestamp.isoformat(),
            'severity': alert.severity,
            'message': alert.message,
            'resource_name': alert.resource.name if alert.resource else 'N/A',
            'metric_name': alert.threshold.metric_definition.name if alert.threshold and alert.threshold.metric_definition else 'N/A',
            'details': alert.details,
            'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None,
            'notified_channels': alert.notified_channels_log
        } for alert in alerts]
        return JsonResponse({'alerts': data})
