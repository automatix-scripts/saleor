# /home/ubuntu/platform-services/monitoring_service/models.py
# Autor: Szymon Fuchs
# Data: 05.10.2021

from django.db import models
from django.db.models import JSONField
from django.utils import timezone

class CloudProviderSettings(models.Model):
    provider_name = models.CharField(max_length=50, unique=True)
    api_key_placeholder = models.CharField(max_length=255, blank=True, null=True)
    api_secret_placeholder = models.CharField(max_length=255, blank=True, null=True)
    additional_config = JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.provider_name

class MonitoredResource(models.Model):
    RESOURCE_TYPES = [
        ('vm', 'Virtual Machine'),
        ('db', 'Database'),
        ('storage', 'Storage Bucket'),
        ('lb', 'Load Balancer'),
        ('custom', 'Custom Service'),
    ]
    name = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=50, choices=RESOURCE_TYPES)
    cloud_identifier = models.CharField(max_length=255, unique=True)
    provider_settings = models.ForeignKey(CloudProviderSettings, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    tags = JSONField(default=dict, blank=True)
    is_monitored = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.resource_type} - {self.cloud_identifier})"

class MetricDefinition(models.Model):
    name = models.CharField(max_length=100, unique=True)
    unit = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.unit})"

class ResourceMetricLog(models.Model):
    resource = models.ForeignKey(MonitoredResource, on_delete=models.CASCADE, related_name='metrics')
    metric_definition = models.ForeignKey(MetricDefinition, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    value = models.FloatField()
    collected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [models.Index(fields=['resource', 'metric_definition', '-timestamp'])]

    def __str__(self):
        return f"{self.resource.name} - {self.metric_definition.name}: {self.value} at {self.timestamp}"

class AlertNotificationChannel(models.Model):
    CHANNEL_TYPES = [('email', 'Email'), ('slack', 'Slack Webhook'), ('custom_webhook', 'Custom Webhook')]
    name = models.CharField(max_length=100)
    channel_type = models.CharField(max_length=50, choices=CHANNEL_TYPES)
    configuration = JSONField(default=dict)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.channel_type})"

class AlertThreshold(models.Model):
    SEVERITY_LEVELS = [('warning', 'Warning'), ('critical', 'Critical')]
    COMPARISON_TYPES = [('gt', 'Greater Than'), ('lt', 'Less Than'), ('gte', 'Greater Than or Equal'), ('lte', 'Less Than or Equal')]

    resource = models.ForeignKey(MonitoredResource, on_delete=models.CASCADE, related_name='thresholds')
    metric_definition = models.ForeignKey(MetricDefinition, on_delete=models.CASCADE)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    comparison_operator = models.CharField(max_length=3, choices=COMPARISON_TYPES, default='gt')
    threshold_value = models.FloatField()
    duration_seconds = models.PositiveIntegerField(default=0, help_text="0 means immediate trigger, otherwise time window in seconds for condition to persist")
    cooldown_seconds = models.PositiveIntegerField(default=300, help_text="Minimum time in seconds before sending another alert for the same condition")
    notification_channels = models.ManyToManyField(AlertNotificationChannel, blank=True)
    is_active = models.BooleanField(default=True)
    last_triggered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.severity.capitalize()} for {self.resource.name} on {self.metric_definition.name} {self.comparison_operator} {self.threshold_value}"

class AlertLog(models.Model):
    resource = models.ForeignKey(MonitoredResource, on_delete=models.CASCADE, null=True, blank=True)
    threshold = models.ForeignKey(AlertThreshold, on_delete=models.SET_NULL, null=True, blank=True)
    severity = models.CharField(max_length=20, choices=AlertThreshold.SEVERITY_LEVELS)
    message = models.TextField()
    details = JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    resolved_at = models.DateTimeField(null=True, blank=True)
    notified_channels_log = JSONField(default=list, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.severity.capitalize()} alert at {self.timestamp}: {self.message}"

class ScalingPolicy(models.Model):
    ACTION_TYPES = [('scale_up', 'Scale Up'), ('scale_down', 'Scale Down')]
    resource_group_identifier = models.CharField(max_length=100, help_text="Identifier for a group of resources or a customer tier")
    metric_definition = models.ForeignKey(MetricDefinition, on_delete=models.CASCADE)
    threshold_value = models.FloatField()
    comparison_operator = models.CharField(max_length=3, choices=AlertThreshold.COMPARISON_TYPES, default='gt')
    duration_seconds = models.PositiveIntegerField(default=300, help_text="Time window in seconds for condition to persist before scaling")
    cooldown_seconds = models.PositiveIntegerField(default=1800, help_text="Minimum time before another scaling action of the same type for this group")
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    action_target_url = models.URLField(max_length=512, help_text="Endpoint to call for scaling action")
    action_payload_template = JSONField(default=dict, blank=True, help_text="JSON template for the action payload")
    is_active = models.BooleanField(default=True)
    last_action_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.action_type} policy for {self.resource_group_identifier} on {self.metric_definition.name}"
