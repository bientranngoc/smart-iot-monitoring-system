"""
Smart Building alert views - BuildingAlert ViewSet
"""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from monitoring.models import BuildingAlert
from monitoring.serializers import BuildingAlertSerializer


class BuildingAlertViewSet(viewsets.ModelViewSet):
    """ViewSet for BuildingAlert management"""
    queryset = BuildingAlert.objects.all()
    serializer_class = BuildingAlertSerializer
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active (unacknowledged) alerts"""
        building_id = request.query_params.get('building')
        
        alerts = BuildingAlert.objects.filter(acknowledged=False)
        if building_id:
            alerts = alerts.filter(zone__building_id=building_id)
        
        alerts = alerts.select_related('zone', 'camera').order_by('-created_at')
        
        serializer = BuildingAlertSerializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge an alert"""
        alert = self.get_object()
        
        # Check if user is authenticated
        if request.user.is_authenticated:
            alert.acknowledged_by = request.user
        
        alert.acknowledged = True
        alert.acknowledged_at = timezone.now()
        alert.save()
        
        return Response({
            'status': 'acknowledged',
            'alert_id': alert.id,
            'acknowledged_at': alert.acknowledged_at
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Alert statistics"""
        building_id = request.query_params.get('building')
        
        alerts = BuildingAlert.objects.all()
        if building_id:
            alerts = alerts.filter(zone__building_id=building_id)
        
        # Last 24 hours
        last_24h = timezone.now() - timedelta(hours=24)
        
        stats = {
            'total': alerts.count(),
            'last_24h': alerts.filter(created_at__gte=last_24h).count(),
            'unacknowledged': alerts.filter(acknowledged=False).count(),
            'by_severity': {
                'EMERGENCY': alerts.filter(severity='EMERGENCY').count(),
                'CRITICAL': alerts.filter(severity='CRITICAL').count(),
                'WARNING': alerts.filter(severity='WARNING').count(),
                'INFO': alerts.filter(severity='INFO').count(),
            },
            'by_type': {}
        }
        
        # Count by alert type
        for alert_type, _ in BuildingAlert.ALERT_TYPE_CHOICES:
            stats['by_type'][alert_type] = alerts.filter(alert_type=alert_type).count()
        
        return Response(stats)
