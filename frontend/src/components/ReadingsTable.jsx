import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';

function ReadingsTable() {
  const [readings, setReadings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    device_id: '',
    limit: 100,
  });

  useEffect(() => {
    fetchReadings();
  }, []);

  const fetchReadings = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filters.device_id) params.device_id = filters.device_id;
      if (filters.limit) params.limit = filters.limit;

      const response = await apiService.getReadings(params);
      setReadings(response.data);
    } catch (error) {
      console.error('Error fetching readings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const handleFilterSubmit = (e) => {
    e.preventDefault();
    fetchReadings();
  };

  const handleReset = () => {
    setFilters({ device_id: '', limit: 100 });
    setTimeout(fetchReadings, 100);
  };

  const exportToCSV = () => {
    const headers = ['Device ID', 'Temperature', 'Humidity', 'Timestamp'];
    const csvData = readings.map(r => [
      r.device_id,
      r.temperature,
      r.humidity,
      new Date(r.timestamp).toLocaleString()
    ]);
    
    const csv = [
      headers.join(','),
      ...csvData.map(row => row.join(','))
    ].join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `readings_${new Date().toISOString()}.csv`;
    a.click();
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
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold text-gray-800 flex items-center">
          <span className="mr-2">📊</span>
          All Readings
        </h2>
        <button
          onClick={exportToCSV}
          className="px-6 py-3 bg-green-500 text-white rounded-lg font-semibold hover:bg-green-600 transition-colors shadow-md hover:shadow-lg"
        >
          📥 Export CSV
        </button>
      </div>

      {/* Filters */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-700 mb-4">Filters</h3>
        <form onSubmit={handleFilterSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Device ID
              </label>
              <input
                type="number"
                name="device_id"
                value={filters.device_id}
                onChange={handleFilterChange}
                placeholder="All devices"
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Limit
              </label>
              <select
                name="limit"
                value={filters.limit}
                onChange={handleFilterChange}
                className="input-field"
              >
                <option value="50">50 readings</option>
                <option value="100">100 readings</option>
                <option value="200">200 readings</option>
                <option value="500">500 readings</option>
              </select>
            </div>
            <div className="flex items-end space-x-2">
              <button type="submit" className="btn-primary flex-1">
                Apply Filters
              </button>
              <button
                type="button"
                onClick={handleReset}
                className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition-colors"
              >
                Reset
              </button>
            </div>
          </div>
        </form>
      </div>

      {/* Readings Table */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-semibold text-gray-700">
            Readings ({readings.length})
          </h3>
          <button
            onClick={fetchReadings}
            className="px-4 py-2 bg-white border-2 border-gray-200 rounded-lg hover:border-primary-500 transition-colors flex items-center space-x-2"
          >
            <span>🔄</span>
            <span>Refresh</span>
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr>
                <th className="table-header rounded-tl-lg">Device ID</th>
                <th className="table-header">Temperature</th>
                <th className="table-header">Humidity</th>
                <th className="table-header rounded-tr-lg">Timestamp</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {readings.length === 0 ? (
                <tr>
                  <td colSpan="4" className="table-cell text-center text-gray-500">
                    No readings found
                  </td>
                </tr>
              ) : (
                readings.map((reading, index) => (
                  <tr key={index} className="hover:bg-gray-50 transition-colors">
                    <td className="table-cell">
                      <span className="font-semibold text-gray-700">
                        Device {reading.device_id}
                      </span>
                    </td>
                    <td className="table-cell">
                      <span className={`text-lg font-bold ${
                        reading.temperature > 27 ? 'text-red-600' :
                        reading.temperature > 23 ? 'text-orange-600' :
                        'text-blue-600'
                      }`}>
                        {reading.temperature}°C
                      </span>
                    </td>
                    <td className="table-cell">
                      <span className={`text-lg font-bold ${
                        reading.humidity > 65 ? 'text-blue-600' :
                        reading.humidity < 45 ? 'text-orange-600' :
                        'text-green-600'
                      }`}>
                        {reading.humidity}%
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
    </div>
  );
}

export default ReadingsTable;
