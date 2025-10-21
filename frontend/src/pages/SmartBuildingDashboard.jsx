import { useState, useEffect } from 'react';
import { Building2, AlertCircle, Zap, Activity, RefreshCw } from 'lucide-react';
import { apiService } from '../services/api';
import ZoneCard from '../components/ZoneCard';

const SmartBuildingDashboard = () => {
  const [building, setBuilding] = useState(null);
  const [zones, setZones] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  // Fetch building data
  const fetchBuildingData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch building info
      const buildingsRes = await apiService.getBuildings();
      if (buildingsRes.data.length > 0) {
        setBuilding(buildingsRes.data[0]);
      }

      // Fetch zones with status
      const zonesRes = await apiService.getZones();
      const zonesWithStatus = await Promise.all(
        zonesRes.data.map(async (zone) => {
          try {
            const statusRes = await apiService.getZoneStatus(zone.id);
            return { ...zone, ...statusRes.data };
          } catch (err) {
            console.error(`Error fetching status for zone ${zone.id}:`, err);
            return zone;
          }
        })
      );
      setZones(zonesWithStatus);

      // Fetch active alerts
      const alertsRes = await apiService.getActiveAlerts();
      setAlerts(alertsRes.data);

      setLastUpdate(new Date());
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load building data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBuildingData();

    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchBuildingData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Calculate building stats
  const calculateStats = () => {
    if (!zones.length) return { avgTemp: 0, totalOccupancy: 0, avgCO2: 0, energyUsage: 0 };

    const avgTemp = zones.reduce((sum, zone) => {
      const temp = zone.sensors?.find(s => s.type === 'TEMPERATURE')?.value || 0;
      return sum + temp;
    }, 0) / zones.length;

    const totalOccupancy = zones.reduce((sum, zone) => {
      const occupancy = zone.sensors?.find(s => s.type === 'OCCUPANCY')?.value || 0;
      return sum + occupancy;
    }, 0);

    const avgCO2 = zones.reduce((sum, zone) => {
      const co2 = zone.sensors?.find(s => s.type === 'CO2')?.value || 0;
      return sum + co2;
    }, 0) / zones.length;

    // Calculate energy usage based on HVAC status
    const energyUsage = zones.reduce((sum, zone) => {
      const hvac = zone.hvac;
      if (!hvac) return sum;
      return sum + (hvac.is_cooling || hvac.is_heating ? 5.5 : 0.5);
    }, 0);

    return { avgTemp, totalOccupancy, avgCO2, energyUsage };
  };

  const stats = calculateStats();

  if (loading && !building) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading Smart Building...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center text-red-600">
          <AlertCircle className="w-16 h-16 mx-auto mb-4" />
          <p className="text-xl font-semibold">{error}</p>
          <button
            onClick={fetchBuildingData}
            className="mt-4 px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Building2 className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {building?.name || 'Smart Building'}
                </h1>
                <p className="text-sm text-gray-500">{building?.address}</p>
              </div>
            </div>

            <button
              onClick={fetchBuildingData}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              disabled={loading}
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>
      </header>

      {/* Stats Overview */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {/* Average Temperature */}
          <div className="bg-white rounded-lg shadow p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Avg Temperature</p>
                <p className="text-2xl font-bold text-gray-900">
                  {stats.avgTemp.toFixed(1)}°C
                </p>
              </div>
              <Activity className="w-10 h-10 text-blue-500" />
            </div>
          </div>

          {/* Total Occupancy */}
          <div className="bg-white rounded-lg shadow p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Occupancy</p>
                <p className="text-2xl font-bold text-gray-900">
                  {stats.totalOccupancy} people
                </p>
              </div>
              <Building2 className="w-10 h-10 text-green-500" />
            </div>
          </div>

          {/* Average CO2 */}
          <div className="bg-white rounded-lg shadow p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Avg CO₂ Level</p>
                <p className="text-2xl font-bold text-gray-900">
                  {stats.avgCO2.toFixed(0)} ppm
                </p>
              </div>
              <Activity className="w-10 h-10 text-purple-500" />
            </div>
          </div>

          {/* Energy Usage */}
          <div className="bg-white rounded-lg shadow p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Energy Usage</p>
                <p className="text-2xl font-bold text-gray-900">
                  {stats.energyUsage.toFixed(1)} kW
                </p>
              </div>
              <Zap className="w-10 h-10 text-yellow-500" />
            </div>
          </div>
        </div>

        {/* Active Alerts */}
        {alerts.length > 0 && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6 rounded-lg">
            <div className="flex items-start">
              <AlertCircle className="w-6 h-6 text-red-600 mr-3 flex-shrink-0" />
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-red-800 mb-2">
                  Active Alerts ({alerts.length})
                </h3>
                <div className="space-y-2">
                  {alerts.slice(0, 3).map((alert) => (
                    <div key={alert.id} className="text-sm text-red-700">
                      <span className="font-medium">{alert.alert_type}:</span> {alert.message}
                      <span className="text-xs text-red-600 ml-2">
                        {new Date(alert.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                  ))}
                </div>
                {alerts.length > 3 && (
                  <p className="text-sm text-red-600 mt-2">
                    +{alerts.length - 3} more alerts
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Zones Grid */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Building Zones</h2>
            <p className="text-sm text-gray-500">
              Last updated: {lastUpdate.toLocaleTimeString()}
            </p>
          </div>

          {zones.length === 0 ? (
            <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
              <Building2 className="w-12 h-12 mx-auto mb-3 text-gray-400" />
              <p>No zones configured</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {zones.map((zone) => (
                <ZoneCard
                  key={zone.id}
                  zone={zone}
                  onZoneClick={(zone) => console.log('Zone clicked:', zone)}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SmartBuildingDashboard;
