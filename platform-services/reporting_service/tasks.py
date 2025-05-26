# /home/ubuntu/platform-services/reporting_service/tasks.py
# Autor: Szymon Fuchs
# Data: 06.09.2021

from django.apps import apps
from django.utils import timezone
from django.core.cache import cache

def shared_task(func=None, **kwargs):
    if func:
        def wrapper(*args, **kwargs_inner):
            print(f"Executing placeholder task: {func.__name__} with args: {args}, kwargs: {kwargs_inner}")
            return func(*args, **kwargs_inner)
        return wrapper
    else:
        def decorator(func_inner):
            def wrapper_dec(*args, **kwargs_inner_dec):
                print(f"Executing placeholder task: {func_inner.__name__} with args: {args}, kwargs: {kwargs_inner_dec}")
                return func_inner(*args, **kwargs_inner_dec)
            return wrapper_dec
        return decorator

@shared_task(name="reporting_service.generate_report_asynchronously")
def generate_report_asynchronously(user_id, report_type, params):
    task_id = generate_report_asynchronously.request.id if hasattr(generate_report_asynchronously, 'request') else f"task_{timezone.now().timestamp()}"
    
    cache.set(f"report_task_{task_id}_status", {"status": "PENDING", "progress": 0, "report_type": report_type}, timeout=3600)
    
    report_data = {"error": "Report generation not fully implemented in placeholder task."}
    
    if report_type == "SalesSummary":
        SalesService = apps.get_model('reporting_service', 'SalesService', require_ready=False)
        try:
            from .services import get_sales_report_for_channel
            report_data = get_sales_report_for_channel(
                user_id,
                params['channel_slug'],
                params['date_from'],
                params['date_to']
            )
        except Exception as e:
            report_data = {"error": f"Failed to generate sales summary: {str(e)}"}

    elif report_type == "ProductPerformance":
        try:
            from .services import get_product_performance_report
            report_data = get_product_performance_report(
                user_id,
                params['channel_slug'],
                params['date_from'],
                params['date_to'],
                params.get('top_n', 10)
            )
        except Exception as e:
            report_data = {"error": f"Failed to generate product performance report: {str(e)}"}
    else:
        report_data = {"error": f"Unknown report type: {report_type}"}


    if "error" in report_data:
        cache.set(f"report_task_{task_id}_status", {"status": "FAILURE", "result": report_data, "report_type": report_type}, timeout=3600)
    else:
        cache.set(f"report_task_{task_id}_result", report_data, timeout=3600)
        cache.set(f"report_task_{task_id}_status", {"status": "SUCCESS", "progress": 100, "report_type": report_type}, timeout=3600)
    
    print(f"Report task {task_id} for {report_type} completed.")
    return report_data
