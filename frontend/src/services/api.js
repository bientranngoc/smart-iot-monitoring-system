import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API Service methods
export const apiService = {
  // Users
  getUsers: () => api.get('/users/'),
  getUser: (id) => api.get(`/users/${id}/`),

  // Devices
  getDevices: () => api.get('/devices/'),
  getDevice: (id) => api.get(`/devices/${id}/`),
  getDeviceReadings: (id, params = {}) => 
    api.get(`/devices/${id}/readings/`, { params }),
  getDeviceLatest: (id) => api.get(`/devices/${id}/latest/`),

  // Readings
  getReadings: (params = {}) => api.get('/readings/', { params }),
  getLatestAll: () => api.get('/readings/latest_all/'),
  getStats: () => api.get('/readings/stats/'),
  
  // OpenSearch
  searchReadings: (params = {}) => api.get('/readings/search/', { params }),
  getAggregations: (params = {}) => api.get('/readings/aggregations/', { params }),
};

export default api;
