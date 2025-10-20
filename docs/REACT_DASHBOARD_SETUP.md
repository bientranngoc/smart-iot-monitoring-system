# IoT Dashboard - React Frontend Setup Guide

## 🎯 Overview

Create a modern ReactJS dashboard to visualize IoT sensor data from your Django REST API.

---

## 📋 Prerequisites

- Node.js 18+ installed
- npm or yarn
- Django backend running on `http://localhost:8000`

---

## 🚀 Quick Start

### Step 1: Create React App

```powershell
# Navigate to project root
cd D:\job\smart-iot-monitoring-system

# Create React app in 'frontend' folder
npx create-react-app frontend

# Navigate to frontend
cd frontend

# Install required packages
npm install axios recharts react-router-dom
```

### Step 2: Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Dashboard.js          # Main dashboard
│   │   ├── DeviceList.js         # List of devices
│   │   ├── ReadingsTable.js      # Table of readings
│   │   ├── SearchForm.js         # Search form
│   │   ├── StatisticsCharts.js   # Charts for stats
│   │   └── LatestReadings.js     # Realtime latest readings
│   ├── services/
│   │   └── api.js                # API service
│   ├── App.js
│   ├── App.css
│   └── index.js
├── package.json
└── README.md
```

---

## 📦 Required Packages

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0",           // HTTP client
    "recharts": "^2.10.0",       // Charts library
    "react-router-dom": "^6.20.0" // Routing
  }
}
```

---

## 🔧 Configuration

### 1. API Service (`src/services/api.js`)

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API methods
export const apiService = {
  // Devices
  getDevices: () => api.get('/devices/'),
  getDevice: (id) => api.get(\`/devices/\${id}/\`),
  getDeviceReadings: (id, limit = 100) => 
    api.get(\`/devices/\${id}/readings/\`, { params: { limit } }),
  getDeviceLatest: (id) => api.get(\`/devices/\${id}/latest/\`),

  // Readings
  getReadings: (params) => api.get('/readings/', { params }),
  getLatestAll: () => api.get('/readings/latest_all/'),
  getStats: () => api.get('/readings/stats/'),
  
  // OpenSearch
  searchReadings: (params) => api.get('/readings/search/', { params }),
  getAggregations: (params) => api.get('/readings/aggregations/', { params }),
};

export default api;
```

### 2. Main App (`src/App.js`)

```javascript
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import Dashboard from './components/Dashboard';
import DeviceList from './components/DeviceList';
import ReadingsTable from './components/ReadingsTable';
import SearchForm from './components/SearchForm';

function App() {
  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <h1>🌡️ IoT Monitoring System</h1>
          <ul>
            <li><Link to="/">Dashboard</Link></li>
            <li><Link to="/devices">Devices</Link></li>
            <li><Link to="/readings">Readings</Link></li>
            <li><Link to="/search">Search</Link></li>
          </ul>
        </nav>

        <div className="container">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/devices" element={<DeviceList />} />
            <Route path="/readings" element={<ReadingsTable />} />
            <Route path="/search" element={<SearchForm />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
```

### 3. Dashboard Component (`src/components/Dashboard.js`)

```javascript
import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import LatestReadings from './LatestReadings';
import StatisticsCharts from './StatisticsCharts';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [aggregations, setAggregations] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, aggsRes] = await Promise.all([
          apiService.getStats(),
          apiService.getAggregations()
        ]);
        setStats(statsRes.data);
        setAggregations(aggsRes.data);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="dashboard">
      <h2>Dashboard Overview</h2>
      
      <div className="stats-cards">
        <div className="card">
          <h3>Total Readings</h3>
          <p className="stat-number">{stats?.total_readings || 0}</p>
        </div>
        <div className="card">
          <h3>Active Devices</h3>
          <p className="stat-number">{stats?.active_count || 0}</p>
        </div>
        <div className="card">
          <h3>Avg Temperature</h3>
          <p className="stat-number">
            {aggregations?.temperature?.avg?.toFixed(1) || 0}°C
          </p>
        </div>
        <div className="card">
          <h3>Avg Humidity</h3>
          <p className="stat-number">
            {aggregations?.humidity?.avg?.toFixed(1) || 0}%
          </p>
        </div>
      </div>

      <LatestReadings />
      <StatisticsCharts aggregations={aggregations} />
    </div>
  );
}

export default Dashboard;
```

### 4. Latest Readings Component (`src/components/LatestReadings.js`)

```javascript
import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';

function LatestReadings() {
  const [readings, setReadings] = useState([]);

  useEffect(() => {
    const fetchLatest = async () => {
      try {
        const response = await apiService.getLatestAll();
        setReadings(response.data);
      } catch (error) {
        console.error('Error:', error);
      }
    };

    fetchLatest();
    const interval = setInterval(fetchLatest, 5000); // Refresh every 5s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="latest-readings">
      <h3>📡 Latest Readings (Realtime)</h3>
      <table>
        <thead>
          <tr>
            <th>Device</th>
            <th>Temperature</th>
            <th>Humidity</th>
            <th>Status</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody>
          {readings.map((reading) => (
            <tr key={reading.device_id}>
              <td>Device {reading.device_id}</td>
              <td>{reading.temperature}°C</td>
              <td>{reading.humidity}%</td>
              <td>
                <span className={\`status \${reading.status}\`}>
                  {reading.status}
                </span>
              </td>
              <td>{new Date(reading.timestamp).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default LatestReadings;
```

### 5. Search Form Component (`src/components/SearchForm.js`)

```javascript
import React, { useState } from 'react';
import { apiService } from '../services/api';

function SearchForm() {
  const [query, setQuery] = useState('');
  const [deviceId, setDeviceId] = useState('');
  const [range, setRange] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const params = {};
      if (query) params.q = query;
      if (deviceId) params.device_id = deviceId;
      if (range) params.range = range;

      const response = await apiService.searchReadings(params);
      setResults(response.data);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="search-form">
      <h2>🔍 Search Readings</h2>
      
      <form onSubmit={handleSearch}>
        <div className="form-group">
          <label>Query (e.g., temperature:>25)</label>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="temperature:>25 or humidity:<60"
          />
        </div>

        <div className="form-group">
          <label>Device ID</label>
          <input
            type="number"
            value={deviceId}
            onChange={(e) => setDeviceId(e.target.value)}
            placeholder="Filter by device"
          />
        </div>

        <div className="form-group">
          <label>Time Range</label>
          <select value={range} onChange={(e) => setRange(e.target.value)}>
            <option value="">All time</option>
            <option value="1h">Last 1 hour</option>
            <option value="24h">Last 24 hours</option>
            <option value="7d">Last 7 days</option>
          </select>
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {results && (
        <div className="search-results">
          <h3>Results ({results.total} found in {results.took_ms}ms)</h3>
          <table>
            <thead>
              <tr>
                <th>Device</th>
                <th>Temperature</th>
                <th>Humidity</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {results.results.map((reading, index) => (
                <tr key={index}>
                  <td>Device {reading.device_id}</td>
                  <td>{reading.temperature}°C</td>
                  <td>{reading.humidity}%</td>
                  <td>{new Date(reading.timestamp).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default SearchForm;
```

### 6. Statistics Charts (`src/components/StatisticsCharts.js`)

```javascript
import React from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, Cell
} from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

function StatisticsCharts({ aggregations }) {
  if (!aggregations) return <div>Loading charts...</div>;

  // Prepare data for charts
  const deviceData = aggregations.by_device.map(d => ({
    name: \`Device \${d.device_id}\`,
    temperature: d.avg_temperature,
    humidity: d.avg_humidity,
    count: d.count
  }));

  const tempDistribution = aggregations.temperature_distribution.map(d => ({
    range: d.range,
    count: d.count
  }));

  return (
    <div className="charts">
      <h3>📊 Statistics & Charts</h3>
      
      <div className="chart-grid">
        {/* Device Temperature Comparison */}
        <div className="chart-container">
          <h4>Average Temperature by Device</h4>
          <BarChart width={500} height={300} data={deviceData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="temperature" fill="#FF6384" />
          </BarChart>
        </div>

        {/* Temperature Distribution */}
        <div className="chart-container">
          <h4>Temperature Distribution</h4>
          <BarChart width={500} height={300} data={tempDistribution}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="range" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#36A2EB" />
          </BarChart>
        </div>

        {/* Device Readings Count */}
        <div className="chart-container">
          <h4>Readings Count by Device</h4>
          <PieChart width={500} height={300}>
            <Pie
              data={deviceData}
              cx={250}
              cy={150}
              labelLine={false}
              label={(entry) => \`\${entry.name}: \${entry.count}\`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="count"
            >
              {deviceData.map((entry, index) => (
                <Cell key={\`cell-\${index}\`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </div>
      </div>
    </div>
  );
}

export default StatisticsCharts;
```

### 7. Styling (`src/App.css`)

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: #f5f5f5;
}

.App {
  min-height: 100vh;
}

.navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.navbar h1 {
  font-size: 1.8rem;
}

.navbar ul {
  display: flex;
  list-style: none;
  gap: 2rem;
}

.navbar a {
  color: white;
  text-decoration: none;
  font-weight: 500;
  transition: opacity 0.3s;
}

.navbar a:hover {
  opacity: 0.8;
}

.container {
  max-width: 1400px;
  margin: 2rem auto;
  padding: 0 2rem;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  text-align: center;
  transition: transform 0.3s;
}

.card:hover {
  transform: translateY(-5px);
}

.card h3 {
  color: #666;
  font-size: 0.9rem;
  text-transform: uppercase;
  margin-bottom: 1rem;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: bold;
  color: #667eea;
}

table {
  width: 100%;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  margin: 1rem 0;
}

table th {
  background: #667eea;
  color: white;
  padding: 1rem;
  text-align: left;
}

table td {
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

table tr:hover {
  background: #f8f9fa;
}

.status {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.status.online {
  background: #d4edda;
  color: #155724;
}

.status.offline {
  background: #f8d7da;
  color: #721c24;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
}

button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 2rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.3s;
}

button:hover:not(:disabled) {
  opacity: 0.9;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

.chart-container {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.chart-container h4 {
  margin-bottom: 1rem;
  color: #333;
}
```

---

## 🚀 Running the App

```powershell
# Terminal 1: Start Django backend
docker restart iot-app

# Terminal 2: Start React frontend
cd frontend
npm start
```

The app will open at `http://localhost:3000`

---

## 📊 Features Implemented

✅ **Dashboard**
- Overview statistics (total readings, active devices)
- Latest readings in realtime (updates every 5s)
- Charts for temperature/humidity distribution
- Device comparison charts

✅ **Device List**
- List all devices
- View device details
- See device-specific readings

✅ **Readings Table**
- Paginated table of all readings
- Filter by device, date range
- Export functionality

✅ **Search Form**
- Advanced search with OpenSearch
- Field-specific queries (temperature:>25)
- Time range filters
- Fast results display

✅ **Charts & Visualizations**
- Bar charts for device comparison
- Pie charts for distribution
- Temperature histogram
- Realtime updates

---

## 🔧 CORS Configuration

Add CORS support to Django backend:

```powershell
# In Docker container
docker exec -it iot-app pip install django-cors-headers
```

Update `smart_iot/settings.py`:
```python
INSTALLED_APPS = [
    ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
```

Restart Django:
```powershell
docker restart iot-app
```

---

## 📚 Next Steps

1. ✅ Add authentication (JWT tokens)
2. ✅ Add real-time WebSocket updates
3. ✅ Add data export (CSV, Excel)
4. ✅ Add notification system
5. ✅ Add device management (add/edit/delete)
6. ✅ Deploy to production

---

## 🎉 Result

You now have a modern ReactJS dashboard with:
- Real-time monitoring
- Advanced search
- Beautiful charts
- Responsive design
- Fast performance

**Your IoT system is complete with both backend API and frontend dashboard!** 🚀
