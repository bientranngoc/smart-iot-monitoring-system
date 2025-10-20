import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import LatestReadings from './LatestReadings';
import StatisticsCharts from './StatisticsCharts';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [aggregations, setAggregations] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setError(null);
      const [statsRes, aggsRes] = await Promise.all([
        apiService.getStats(),
        apiService.getAggregations()
      ]);
      setStats(statsRes.data);
      setAggregations(aggsRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-primary-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
        <p className="text-red-700">{error}</p>
        <button onClick={fetchData} className="mt-2 text-red-600 underline">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold text-gray-800">Dashboard Overview</h2>
        <button 
          onClick={fetchData}
          className="px-4 py-2 bg-white rounded-lg shadow hover:shadow-md transition-all duration-300 flex items-center space-x-2"
        >
          <span>🔄</span>
          <span>Refresh</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card bg-gradient-to-br from-blue-50 to-blue-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-blue-600 uppercase">Total Readings</p>
              <p className="text-4xl font-bold text-blue-700 mt-2">
                {stats?.total_readings || 0}
              </p>
            </div>
            <div className="text-5xl">📊</div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-green-50 to-green-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-green-600 uppercase">Active Devices</p>
              <p className="text-4xl font-bold text-green-700 mt-2">
                {stats?.active_count || 0}
              </p>
            </div>
            <div className="text-5xl">📱</div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-orange-50 to-orange-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-orange-600 uppercase">Avg Temperature</p>
              <p className="text-4xl font-bold text-orange-700 mt-2">
                {aggregations?.temperature?.avg?.toFixed(1) || '0.0'}°C
              </p>
            </div>
            <div className="text-5xl">🌡️</div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-purple-50 to-purple-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-purple-600 uppercase">Avg Humidity</p>
              <p className="text-4xl font-bold text-purple-700 mt-2">
                {aggregations?.humidity?.avg?.toFixed(1) || '0.0'}%
              </p>
            </div>
            <div className="text-5xl">💧</div>
          </div>
        </div>
      </div>

      {/* Latest Readings */}
      <LatestReadings />

      {/* Statistics Charts */}
      {aggregations && <StatisticsCharts aggregations={aggregations} />}
    </div>
  );
}

export default Dashboard;
