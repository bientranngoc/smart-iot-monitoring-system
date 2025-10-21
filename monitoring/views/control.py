"""
Smart Building control views - HVAC ViewSet
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from monitoring.models import HVACControl
from monitoring.serializers import HVACControlSerializer


class HVACControlViewSet(viewsets.ModelViewSet):
    """ViewSet for HVAC Control management"""
    queryset = HVACControl.objects.all()
    serializer_class = HVACControlSerializer
    
    @action(detail=True, methods=['post'])
    def set_mode(self, request, pk=None):
        """Change HVAC mode"""
        hvac = self.get_object()
        mode = request.data.get('mode')
        
        if mode not in ['AUTO', 'MANUAL', 'SCHEDULE', 'OFF']:
            return Response(
                {'error': 'Invalid mode. Valid options: AUTO, MANUAL, SCHEDULE, OFF'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        hvac.mode = mode
        hvac.save()
        
        return Response({
            'status': 'success',
            'hvac_id': hvac.id,
            'zone': hvac.zone.name,
            'mode': hvac.mode,
            'message': f'HVAC mode changed to {mode}'
        })
    
    @action(detail=True, methods=['post'])
    def set_temperature(self, request, pk=None):
        """Set target temperature (MANUAL mode only)"""
        hvac = self.get_object()
        
        if hvac.mode != 'MANUAL':
            return Response(
                {'error': f'Can only set temperature in MANUAL mode (current: {hvac.mode})'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        temperature = request.data.get('temperature')
        if not temperature:
            return Response(
                {'error': 'temperature parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            temp_value = float(temperature)
            if temp_value < 16 or temp_value > 32:
                return Response(
                    {'error': 'Temperature must be between 16°C and 32°C'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            hvac.set_temperature = temp_value
            hvac.save()
            
            return Response({
                'status': 'success',
                'hvac_id': hvac.id,
                'zone': hvac.zone.name,
                'set_temperature': hvac.set_temperature,
                'message': f'Target temperature set to {temp_value}°C'
            })
            
        except ValueError:
            return Response(
                {'error': 'Invalid temperature value'},
                status=status.HTTP_400_BAD_REQUEST
            )
