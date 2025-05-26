# /home/ubuntu/platform-services/reporting_service/views.py
# Autor: Szymon Fuchs
# Data: 06.09.2021

from django.http import JsonResponse
from django.views import View
import json
from datetime import datetime, date
from .services import get_sales_report_for_channel, get_product_performance_report
from .tasks import generate_report_asynchronously
from django.core.cache import cache
from django.utils import timezone


def parse_dates(date_from_str, date_to_str):
    try:
        date_from = datetime.strptime(date_from_str, "%Y-%m-%d").date()
        date_to = datetime.strptime(date_to_str, "%Y-%m-%d").date()
        if date_from > date_to:
            return None, None, {'error': 'date_from cannot be after date_to'}
        return date_from, date_to, None
    except ValueError:
        return None, None, {'error': 'Invalid date format. Use YYYY-MM-DD.'}

class BaseReportView(View):
    async def get_common_params(self, request_body_data):
        user_id = request_body_data.get('user_id')
        channel_slug = request_body_data.get('channel_slug')
        date_from_str = request_body_data.get('date_from')
        date_to_str = request_body_data.get('date_to')

        if not all([user_id, channel_slug, date_from_str, date_to_str]):
            return None, {'error': 'Missing required fields: user_id, channel_slug, date_from, date_to'}

        date_from, date_to, error = parse_dates(date_from_str, date_to_str)
        if error:
            return None, error
            
        return {
            'user_id': user_id,
            'channel_slug': channel_slug,
            'date_from': date_from,
            'date_to': date_to
        }, None

class SalesReportView(BaseReportView):
    async def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        common_params, error = await self.get_common_params(data)
        if error:
            return JsonResponse(error, status=400)

        report_data = await get_sales_report_for_channel(
            common_params['user_id'],
            common_params['channel_slug'],
            common_params['date_from'],
            common_params['date_to']
        )

        if "error" in report_data:
             return JsonResponse(report_data, status=403 if report_data.get("error") == "Unauthorized access to channel" else 500)

        return JsonResponse(report_data)

class ProductPerformanceReportView(BaseReportView):
    async def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        common_params, error = await self.get_common_params(data)
        if error:
            return JsonResponse(error, status=400)
        
        top_n = data.get('top_n', 10)
        try:
            top_n = int(top_n)
            if not (1 <= top_n <= 100):
                raise ValueError("top_n out of range")
        except ValueError:
            return JsonResponse({'error': 'Invalid top_n value, must be an integer between 1 and 100.'}, status=400)


        report_data = await get_product_performance_report(
            common_params['user_id'],
            common_params['channel_slug'],
            common_params['date_from'],
            common_params['date_to'],
            top_n=top_n
        )

        if "error" in report_data:
             return JsonResponse(report_data, status=500)
        return JsonResponse(report_data)

class AsyncReportRequestView(BaseReportView):
    async def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        report_type = data.get('report_type')
        if not report_type or report_type not in ["SalesSummary", "ProductPerformance"]:
            return JsonResponse({'error': 'Missing or invalid report_type. Supported: SalesSummary, ProductPerformance'}, status=400)

        common_params, error = await self.get_common_params(data)
        if error:
            return JsonResponse(error, status=400)
        
        task_params = {
            'channel_slug': common_params['channel_slug'],
            'date_from': common_params['date_from'],
            'date_to': common_params['date_to'],
        }
        if report_type == "ProductPerformance":
            task_params['top_n'] = data.get('top_n', 10)

        task = generate_report_asynchronously.delay(common_params['user_id'], report_type, task_params)
        
        task_id_to_return = task.id if hasattr(task, 'id') else f"emulated_task_{timezone.now().timestamp()}"
        
        cache.set(f"report_task_{task_id_to_return}_status", {"status": "QUEUED", "report_type": report_type}, timeout=3600)


        return JsonResponse({'message': 'Report generation started.', 'task_id': task_id_to_return}, status=202)

class AsyncReportStatusView(View):
    async def get(self, request, task_id, *args, **kwargs):
        status_data = cache.get(f"report_task_{task_id}_status")
        
        if not status_data:
            return JsonResponse({'error': 'Report task not found or expired.'}, status=404)
        
        response_data = {"task_id": task_id, "status": status_data.get("status"), "report_type": status_data.get("report_type")}

        if status_data.get("status") == "SUCCESS":
            result_data = cache.get(f"report_task_{task_id}_result")
            if result_data:
                response_data["result"] = result_data
            else:
                response_data["status"] = "PROCESSING_RESULT" # Result might be large, still being fetched
        elif status_data.get("status") == "FAILURE":
            failure_details = cache.get(f"report_task_{task_id}_status", {}).get('result', {})
            response_data["error_details"] = failure_details


        return JsonResponse(response_data)
