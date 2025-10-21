import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SmartBuildingDashboard from './pages/SmartBuildingDashboard';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<SmartBuildingDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;
