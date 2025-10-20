import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';

function DeviceList() {
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [deviceReadings, setDeviceReadings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [readingsLoading, setReadingsLoading] = useState(false);

  useEffect(() => {
    fetchDevices();
  }, []);

  const fetchDevices = async () => {
    try {
      const response = await apiService.getDevices();
      setDevices(response.data);
    } catch (error) {
      console.error('Error fetching devices:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeviceClick = async (device) => {
    setSelectedDevice(device);
    setReadingsLoading(true);
    try {
      const response = await apiService.getDeviceReadings(device.id, { limit: 50 });
      setDeviceReadings(response.data);
    } catch (error) {
      console.error('Error fetching device readings:', error);
    } finally {
      setReadingsLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-gray-800 flex items-center">
        <span className="mr-2">📱</span>
        Device Management
      </h2>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Devices List */}
        <div className="lg:col-span-1">
          <div className="card">
            <h3 className="text-xl font-semibold text-gray-700 mb-4">
              All Devices ({devices.length})
            </h3>
            <div className="space-y-2">
              {devices.map((device) => (
                <button
                  key={device.id}
                  onClick={() => handleDeviceClick(device)}
                  className={`w-full text-left p-4 rounded-lg transition-all duration-300 ${
                    selectedDevice?.id === device.id
                      ? 'bg-gradient-to-r from-primary-500 to-secondary-500 text-white shadow-lg'
                      : 'bg-gray-50 hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className={`font-semibold ${
                        selectedDevice?.id === device.id ? 'text-white' : 'text-gray-800'
                      }`}>
                        {device.name}
                      </p>
                      <p className={`text-sm ${
                        selectedDevice?.id === device.id ? 'text-gray-100' : 'text-gray-500'
                      }`}>
                        Location: {device.location}
                      </p>
                    </div>
                    <span className={`badge ${
                      device.is_active ? 'badge-success' : 'badge-danger'
                    }`}>
                      {device.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Device Details & Readings */}
        <div className="lg:col-span-2">
          {selectedDevice ? (
            <div className="space-y-6">
              {/* Device Info Card */}
              <div className="card bg-gradient-to-r from-primary-50 to-secondary-50">
                <h3 className="text-2xl font-bold text-gray-800 mb-4">
                  {selectedDevice.name}
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Device ID</p>
                    <p className="text-lg font-semibold text-gray-800">{selectedDevice.id}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Location</p>
                    <p className="text-lg font-semibold text-gray-800">{selectedDevice.location}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Owner</p>
                    <p className="text-lg font-semibold text-gray-800">User #{selectedDevice.user}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Status</p>
                    <span className={`badge ${
                      selectedDevice.is_active ? 'badge-success' : 'badge-danger'
                    }`}>
                      {selectedDevice.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Readings Table */}
              <div className="card">
                <h3 className="text-xl font-semibold text-gray-700 mb-4">
                  Recent Readings (Last 50)
                </h3>
                
                {readingsLoading ? (
                  <div className="flex items-center justify-center h-32">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-primary-500"></div>
                  </div>
                ) : deviceReadings.length === 0 ? (
                  <div className="text-center py-12">
                    <p className="text-gray-500">No readings available for this device</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full">
                      <thead>
                        <tr>
                          <th className="table-header rounded-tl-lg">Temperature</th>
                          <th className="table-header">Humidity</th>
                          <th className="table-header rounded-tr-lg">Timestamp</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {deviceReadings.map((reading, index) => (
                          <tr key={index} className="hover:bg-gray-50 transition-colors">
                            <td className="table-cell">
                              <span className="text-lg font-bold text-orange-600">
                                {reading.temperature}°C
                              </span>
                            </td>
                            <td className="table-cell">
                              <span className="text-lg font-bold text-blue-600">
                                {reading.humidity}%
                              </span>
                            </td>
                            <td className="table-cell text-gray-600">
                              {new Date(reading.timestamp).toLocaleString()}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="card h-full flex items-center justify-center">
              <div className="text-center">
                <span className="text-6xl mb-4 block">📱</span>
                <p className="text-xl text-gray-500">Select a device to view details</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default DeviceList;
