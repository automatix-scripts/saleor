# /home/ubuntu/platform-services/monitoring_service/tasks.py
# Autor: Szymon Fuchs
# Data: 05.10.2021

from django.apps import apps
from django.utils import timezone
from datetime import timedelta

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


def get_cloud_provider_instance(provider_settings_obj):
    if provider_settings_obj.provider_name.lower() == 'aws':
        try:
            from .cloud_integrations.aws_provider import AWSMetricsProvider
            return AWSMetricsProvider(provider_settings_obj)
        except ImportError:
            print(f"Could not import AWSMetricsProvider for {provider_settings_obj.provider_name}")
            return None
    print(f"No provider implementation for {provider_settings_obj.provider_name}")
    return None

def get_notifier_instance(channel_obj):
    if channel_obj.channel_type == 'email':
        try:
            from .alerting.email_notifier import EmailAlertNotifier
            return EmailAlertNotifier(channel_obj.configuration)
        except ImportError:
            print(f"Could not import EmailAlertNotifier for {channel_obj.name}")
            return None
    print(f"No notifier implementation for {channel_obj.channel_type}")
    return None


@shared_task(name="monitoring_service.fetch_and_evaluate_metrics")
def fetch_and_evaluate_metrics():
    MonitoredResource = apps.get_model('monitoring_service', 'MonitoredResource')
    ResourceMetricLog = apps.get_model('monitoring_service', 'ResourceMetricLog')
    MetricDefinition = apps.get_model('monitoring_service', 'MetricDefinition')
    AlertThreshold = apps.get_model('monitoring_service', 'AlertThreshold')
    ScalingPolicy = apps.get_model('monitoring_service', 'ScalingPolicy')

    print("Starting fetch_and_evaluate_metrics task...")
    for resource in MonitoredResource.objects.filter(is_monitored=True, provider_settings__is_active=True):
        if not resource.provider_settings:
            print(f"Resource {resource.name} has no provider settings, skipping.")
            continue
        
        provider_instance = get_cloud_provider_instance(resource.provider_settings)
        if not provider_instance:
            print(f"No provider instance for {resource.provider_settings.provider_name}, skipping resource {resource.name}")
            continue

        metric_defs_to_fetch = {md.name: md for md in MetricDefinition.objects.all()}
        
        fetched_metrics_data = provider_instance.get_metrics(resource.cloud_identifier, metric_defs_to_fetch)
        
        if not fetched_metrics_data and 'cpu_utilization_percent' in metric_defs_to_fetch :
             fetched_metrics_data.append({
                 'metric_definition_id': metric_defs_to_fetch['cpu_utilization_percent'].id,
                 'value': 75.5, 
                 'timestamp': timezone.now()
             })
        
        for metric_data in fetched_metrics_data:
            try:
                metric_def_obj = MetricDefinition.objects.get(id=metric_data['metric_definition_id'])
                ResourceMetricLog.objects.create(
                    resource=resource,
                    metric_definition=metric_def_obj,
                    value=metric_data['value'],
                    timestamp=metric_data.get('timestamp', timezone.now())
                )
                print(f"Logged metric {metric_def_obj.name} for {resource.name}: {metric_data['value']}")
                
                check_alert_thresholds(resource, metric_def_obj, metric_data['value'])
                check_scaling_policies(resource, metric_def_obj, metric_data['value'])

            except MetricDefinition.DoesNotExist:
                print(f"MetricDefinition with id {metric_data['metric_definition_id']} not found.")
            except Exception as e:
                print(f"Error processing metric for {resource.name}: {str(e)}")
    print("Finished fetch_and_evaluate_metrics task.")


def check_alert_thresholds(resource, metric_def, current_value):
    AlertThreshold = apps.get_model('monitoring_service', 'AlertThreshold')
    now = timezone.now()
    thresholds = AlertThreshold.objects.filter(
        resource=resource, 
        metric_definition=metric_def, 
        is_active=True
    )
    for threshold in thresholds:
        condition_met = False
        if threshold.comparison_operator == 'gt' and current_value > threshold.threshold_value: condition_met = True
        elif threshold.comparison_operator == 'lt' and current_value < threshold.threshold_value: condition_met = True
        elif threshold.comparison_operator == 'gte' and current_value >= threshold.threshold_value: condition_met = True
        elif threshold.comparison_operator == 'lte' and current_value <= threshold.threshold_value: condition_met = True
        
        if condition_met:
            if threshold.last_triggered_at is None or (now - threshold.last_triggered_at) > timedelta(seconds=threshold.cooldown_seconds):
                print(f"Condition met for threshold {threshold.id} on {resource.name}. Triggering alert.")
                trigger_alert.delay(
                    threshold_id=threshold.id,
                    resource_id=resource.id,
                    current_value=current_value,
                    message_override=f"{metric_def.name} for {resource.name} is {current_value}{metric_def.unit}, exceeding threshold of {threshold.threshold_value}{metric_def.unit}."
                )
                threshold.last_triggered_at = now
                threshold.save(update_fields=['last_triggered_at'])
            else:
                print(f"Threshold {threshold.id} condition met but in cooldown period.")

@shared_task(name="monitoring_service.trigger_alert")
def trigger_alert(threshold_id, resource_id, current_value, message_override=None):
    AlertThreshold = apps.get_model('monitoring_service', 'AlertThreshold')
    MonitoredResource = apps.get_model('monitoring_service', 'MonitoredResource')
    AlertLog = apps.get_model('monitoring_service', 'AlertLog')
    
    try:
        threshold = AlertThreshold.objects.get(id=threshold_id)
        resource = MonitoredResource.objects.get(id=resource_id)
    except (AlertThreshold.DoesNotExist, MonitoredResource.DoesNotExist) as e:
        print(f"Cannot trigger alert, threshold or resource not found: {str(e)}")
        return

    message = message_override or f"Alert for {resource.name}: {threshold.metric_definition.name} is {current_value}{threshold.metric_definition.unit} (Threshold: {threshold.comparison_operator} {threshold.threshold_value}{threshold.metric_definition.unit})"
    details = {
        'resource_name': resource.name,
        'metric': threshold.metric_definition.name,
        'current_value': current_value,
        'threshold_value': threshold.threshold_value,
        'comparison': threshold.comparison_operator
    }
    
    alert_log_entry = AlertLog.objects.create(
        resource=resource,
        threshold=threshold,
        severity=threshold.severity,
        message=message,
        details=details
    )
    print(f"Created AlertLog entry: {alert_log_entry.id}")

    notified_list = []
    for channel in threshold.notification_channels.filter(is_active=True):
        notifier = get_notifier_instance(channel)
        if notifier:
            subject = f"{threshold.severity.upper()} Alert: {resource.name} - {threshold.metric_definition.name}"
            success = notifier.send_alert(subject, message, details)
            if success:
                notified_list.append(f"{channel.name} ({channel.channel_type})")
    
    if notified_list:
        alert_log_entry.notified_channels_log = notified_list
        alert_log_entry.save(update_fields=['notified_channels_log'])


def check_scaling_policies(resource, metric_def, current_value):
    ScalingPolicy = apps.get_model('monitoring_service', 'ScalingPolicy')
    now = timezone.now()
    policies = ScalingPolicy.objects.filter(
        resource_group_identifier=resource.name, 
        metric_definition=metric_def,
        is_active=True
    )
    for policy in policies:
        condition_met = False
        if policy.comparison_operator == 'gt' and current_value > policy.threshold_value: condition_met = True
        elif policy.comparison_operator == 'lt' and current_value < policy.threshold_value: condition_met = True
        elif policy.comparison_operator == 'gte' and current_value >= policy.threshold_value: condition_met = True
        elif policy.comparison_operator == 'lte' and current_value <= policy.threshold_value: condition_met = True
        
        if condition_met:
            if policy.last_action_at is None or (now - policy.last_action_at) > timedelta(seconds=policy.cooldown_seconds):
                print(f"Condition met for scaling policy {policy.id} for {resource.name}. Triggering scaling action.")
                trigger_scaling_action.delay(policy.id, current_value)
                policy.last_action_at = now
                policy.save(update_fields=['last_action_at'])
            else:
                print(f"Scaling policy {policy.id} condition met but in cooldown period.")

@shared_task(name="monitoring_service.trigger_scaling_action")
def trigger_scaling_action(policy_id, current_metric_value):
    ScalingPolicy = apps.get_model('monitoring_service', 'ScalingPolicy')
    try:
        policy = ScalingPolicy.objects.get(id=policy_id)
    except ScalingPolicy.DoesNotExist:
        print(f"ScalingPolicy with id {policy_id} not found.")
        return

    payload = dict(policy.action_payload_template) 
    payload.update({
        'policy_id': policy.id,
        'action_type': policy.action_type,
        'resource_group_identifier': policy.resource_group_identifier,
        'metric_name': policy.metric_definition.name,
        'current_metric_value': current_metric_value,
        'timestamp': timezone.now().isoformat()
    })
    
    print(f"Placeholder: Triggering scaling action for policy {policy.id} to URL {policy.action_target_url} with payload: {payload}")
