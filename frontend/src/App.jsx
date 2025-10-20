import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import DeviceList from './components/DeviceList';
import ReadingsTable from './components/ReadingsTable';
import SearchForm from './components/SearchForm';

function Navigation() {
  const location = useLocation();
  
  const isActive = (path) => location.pathname === path;
  
  return (
    <nav className="bg-gradient-to-r from-primary-500 to-secondary-500 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-white flex items-center">
              <span className="text-3xl mr-2">🌡️</span>
              IoT Monitoring System
            </h1>
          </div>
          <div className="flex space-x-8">
            <Link 
              to="/" 
              className={`nav-link ${isActive('/') ? 'border-b-2 border-white' : ''}`}
            >
              Dashboard
            </Link>
            <Link 
              to="/devices" 
              className={`nav-link ${isActive('/devices') ? 'border-b-2 border-white' : ''}`}
            >
              Devices
            </Link>
            <Link 
              to="/readings" 
              className={`nav-link ${isActive('/readings') ? 'border-b-2 border-white' : ''}`}
            >
              Readings
            </Link>
            <Link 
              to="/search" 
              className={`nav-link ${isActive('/search') ? 'border-b-2 border-white' : ''}`}
            >
              Search
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
