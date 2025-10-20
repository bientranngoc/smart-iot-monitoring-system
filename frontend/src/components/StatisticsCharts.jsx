import React from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a'];

function StatisticsCharts({ aggregations }) {
  if (!aggregations) return null;

  // Prepare data for charts
  const deviceData = aggregations.by_device?.map(d => ({
    name: `Device ${d.device_id}`,
    temperature: parseFloat(d.avg_temperature.toFixed(1)),
    humidity: parseFloat(d.avg_humidity.toFixed(1)),
    count: d.count
  })) || [];

  const tempDistribution = aggregations.temperature_distribution?.map(d => ({
    range: d.range,
    count: d.count
  })) || [];

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 rounded-lg shadow-lg border border-gray-200">
          <p className="font-semibold text-gray-800">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }} className="text-sm">
              {entry.name}: {entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-6">
      <h3 className="text-2xl font-bold text-gray-800 flex items-center">
        <span className="mr-2">📊</span>
        Statistics & Analytics
      </h3>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Average Temperature by Device */}
        <div className="card">
          <h4 className="text-lg font-semibold text-gray-700 mb-4">
            🌡️ Average Temperature by Device
          </h4>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={deviceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="name" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Bar 
                dataKey="temperature" 
                fill="#f97316" 
                radius={[8, 8, 0, 0]}
                name="Temperature (°C)"
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Average Humidity by Device */}
        <div className="card">
          <h4 className="text-lg font-semibold text-gray-700 mb-4">
            💧 Average Humidity by Device
          </h4>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={deviceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="name" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Bar 
                dataKey="humidity" 
                fill="#3b82f6" 
                radius={[8, 8, 0, 0]}
                name="Humidity (%)"
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Temperature Distribution */}
        <div className="card">
          <h4 className="text-lg font-semibold text-gray-700 mb-4">
            📈 Temperature Distribution
          </h4>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={tempDistribution}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="range" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip content={<CustomTooltip />} />
              <Bar 
                dataKey="count" 
                fill="#667eea" 
                radius={[8, 8, 0, 0]}
                name="Count"
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Readings Count by Device (Pie Chart) */}
        <div className="card">
          <h4 className="text-lg font-semibold text-gray-700 mb-4">
            📊 Readings Distribution by Device
          </h4>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={deviceData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, count }) => `${name}: ${count}`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="count"
              >
                {deviceData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Temperature & Humidity Comparison */}
        <div className="card lg:col-span-2">
          <h4 className="text-lg font-semibold text-gray-700 mb-4">
            📉 Temperature & Humidity Comparison by Device
          </h4>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={deviceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="name" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="temperature" 
                stroke="#f97316" 
                strokeWidth={3}
                name="Temperature (°C)"
                dot={{ fill: '#f97316', r: 5 }}
              />
              <Line 
                type="monotone" 
                dataKey="humidity" 
                stroke="#3b82f6" 
                strokeWidth={3}
                name="Humidity (%)"
                dot={{ fill: '#3b82f6', r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-orange-50 p-4 rounded-lg border-l-4 border-orange-500">
          <p className="text-sm text-orange-600 font-medium">Temperature Range</p>
          <p className="text-xl font-bold text-orange-700">
            {aggregations.temperature?.min?.toFixed(1)}°C - {aggregations.temperature?.max?.toFixed(1)}°C
          </p>
        </div>
        <div className="bg-blue-50 p-4 rounded-lg border-l-4 border-blue-500">
          <p className="text-sm text-blue-600 font-medium">Humidity Range</p>
          <p className="text-xl font-bold text-blue-700">
            {aggregations.humidity?.min?.toFixed(1)}% - {aggregations.humidity?.max?.toFixed(1)}%
          </p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg border-l-4 border-green-500">
          <p className="text-sm text-green-600 font-medium">Total Documents</p>
          <p className="text-xl font-bold text-green-700">
            {aggregations.total_documents}
          </p>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg border-l-4 border-purple-500">
          <p className="text-sm text-purple-600 font-medium">Query Time</p>
          <p className="text-xl font-bold text-purple-700">
            {aggregations.query_time_ms}ms
          </p>
        </div>
      </div>
    </div>
  );
}

export default StatisticsCharts;
