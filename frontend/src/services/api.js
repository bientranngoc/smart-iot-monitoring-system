import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Smart Building API Service
export const apiService = {
  // Buildings
  getBuildings: () => api.get('/buildings/'),
  getBuilding: (id) => api.get(`/buildings/${id}/`),
  
  // Zones
  getZones: () => api.get('/zones/'),
  getZone: (id) => api.get(`/zones/${id}/`),
  getZoneStatus: (id) => api.get(`/zones/${id}/status/`),
  
  // Alerts (Building Alerts)
  getAlerts: (params = {}) => api.get('/building-alerts/', { params }),
  getActiveAlerts: () => api.get('/building-alerts/?status=active'),
  acknowledgeAlert: (id) => api.post(`/building-alerts/${id}/acknowledge/`),
  
  // HVAC Controls
  getHVACControls: () => api.get('/hvac-controls/'),
  updateHVACControl: (id, data) => api.patch(`/hvac-controls/${id}/`, data),
  
  // Energy Logs
  getEnergyLogs: (params = {}) => api.get('/energy-logs/', { params }),
};

export default api;
