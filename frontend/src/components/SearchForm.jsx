import React, { useState } from 'react';
import { apiService } from '../services/api';

function SearchForm() {
  const [query, setQuery] = useState('');
  const [deviceId, setDeviceId] = useState('');
  const [range, setRange] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const params = {};
      if (query) params.q = query;
      if (deviceId) params.device_id = deviceId;
      if (range) params.range = range;

      const response = await apiService.searchReadings(params);
      setResults(response.data);
    } catch (error) {
      console.error('Search error:', error);
      setError('Failed to search. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setQuery('');
    setDeviceId('');
    setRange('');
    setResults(null);
    setError(null);
  };

  const exampleQueries = [
    { label: 'Temperature > 25°C', value: 'temperature:>25' },
    { label: 'Humidity < 60%', value: 'humidity:<60' },
    { label: 'Temperature between 20-25°C', value: 'temperature:>=20 AND temperature:<=25' },
  ];

  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="text-3xl font-bold text-gray-800 flex items-center mb-6">
          <span className="mr-2">🔍</span>
          Advanced Search
        </h2>

        <form onSubmit={handleSearch} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Query
            </label>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., temperature:>25 or humidity:<60"
              className="input-field"
            />
            <div className="mt-2 flex flex-wrap gap-2">
              <span className="text-sm text-gray-600">Examples:</span>
              {exampleQueries.map((example, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => setQuery(example.value)}
                  className="text-xs bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded-full transition-colors"
                >
                  {example.label}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Device ID (Optional)
              </label>
              <input
                type="number"
                value={deviceId}
                onChange={(e) => setDeviceId(e.target.value)}
                placeholder="Filter by device ID"
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Time Range (Optional)
              </label>
              <select
                value={range}
                onChange={(e) => setRange(e.target.value)}
                className="input-field"
              >
                <option value="">All time</option>
                <option value="1h">Last 1 hour</option>
                <option value="24h">Last 24 hours</option>
                <option value="7d">Last 7 days</option>
              </select>
            </div>
          </div>

          <div className="flex space-x-4">
            <button type="submit" disabled={loading} className="btn-primary flex-1">
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Searching...
                </span>
              ) : (
                '🔍 Search'
              )}
            </button>
            <button
              type="button"
              onClick={handleClear}
              className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition-colors"
            >
              Clear
            </button>
          </div>
        </form>

        {error && (
          <div className="mt-4 bg-red-50 border-l-4 border-red-500 p-4 rounded">
            <p className="text-red-700">{error}</p>
          </div>
        )}
      </div>

      {results && (
        <div className="card">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-2xl font-bold text-gray-800">
              Search Results
            </h3>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Found <span className="font-bold text-primary-600">{results.total}</span> results
              </span>
              <span className="text-sm text-gray-600">
                in <span className="font-bold text-green-600">{results.took_ms}ms</span>
              </span>
            </div>
          </div>

          {results.results.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg">No results found</p>
              <p className="text-gray-400 mt-2">Try adjusting your search criteria</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr>
                    <th className="table-header rounded-tl-lg">Device</th>
                    <th className="table-header">Temperature</th>
                    <th className="table-header">Humidity</th>
                    <th className="table-header rounded-tr-lg">Timestamp</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {results.results.map((reading, index) => (
                    <tr key={index} className="hover:bg-gray-50 transition-colors">
                      <td className="table-cell">
                        <span className="font-semibold text-gray-700">
                          Device {reading.device_id}
                        </span>
                      </td>
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
      )}
    </div>
  );
}

export default SearchForm;
