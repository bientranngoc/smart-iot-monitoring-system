import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';

function LatestReadings() {
  const [readings, setReadings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLatest();
    const interval = setInterval(fetchLatest, 5000); // Refresh every 5s
    return () => clearInterval(interval);
  }, []);

  const fetchLatest = async () => {
    try {
      const response = await apiService.getLatestAll();
      setReadings(response.data);
    } catch (error) {
      console.error('Error fetching latest readings:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    return status === 'online' ? 'badge-success' : 'badge-danger';
  };

  const getTemperatureColor = (temp) => {
    if (temp > 27) return 'text-red-600 font-bold';
    if (temp > 23) return 'text-orange-600';
    return 'text-blue-600';
  };

  const getHumidityColor = (humidity) => {
    if (humidity > 65) return 'text-blue-600 font-bold';
    if (humidity < 45) return 'text-orange-600';
    return 'text-green-600';
  };

  if (loading) {
    return (
      <div className="card">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="space-y-2">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-2xl font-bold text-gray-800 flex items-center">
          <span className="mr-2">📡</span>
          Latest Readings (Realtime)
        </h3>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-600">Live - Updates every 5s</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full">
          <thead>
            <tr>
              <th className="table-header rounded-tl-lg">Device</th>
              <th className="table-header">Temperature</th>
              <th className="table-header">Humidity</th>
              <th className="table-header">Status</th>
              <th className="table-header rounded-tr-lg">Last Update</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {readings.length === 0 ? (
              <tr>
                <td colSpan="5" className="table-cell text-center text-gray-500">
                  No readings available
                </td>
              </tr>
            ) : (
              readings.map((reading) => (
                <tr key={reading.device_id} className="hover:bg-gray-50 transition-colors">
                  <td className="table-cell">
                    <div className="flex items-center space-x-2">
                      <span className="text-2xl">📱</span>
                      <span className="font-semibold text-gray-700">
                        Device {reading.device_id}
                      </span>
                    </div>
                  </td>
                  <td className="table-cell">
                    <span className={`text-2xl font-bold ${getTemperatureColor(reading.temperature)}`}>
                      {reading.temperature}°C
                    </span>
                  </td>
                  <td className="table-cell">
                    <span className={`text-2xl font-bold ${getHumidityColor(reading.humidity)}`}>
                      {reading.humidity}%
                    </span>
                  </td>
                  <td className="table-cell">
                    <span className={`badge ${getStatusColor(reading.status)}`}>
                      {reading.status}
                    </span>
                  </td>
                  <td className="table-cell text-gray-600">
                    {new Date(reading.timestamp).toLocaleString()}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default LatestReadings;
