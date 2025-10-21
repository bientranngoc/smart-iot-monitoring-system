import { useState, useEffect } from 'react';
import { Thermometer, Droplets, Wind, Users, Video, AlertTriangle } from 'lucide-react';
import LiveCameraView from './LiveCameraView';

const ZoneCard = ({ zone, onZoneClick }) => {
  const [showCamera, setShowCamera] = useState(false);

  // Get sensor values (API returns sensors array with type, value)
  const temperature = zone.sensors?.find(s => s.type === 'TEMPERATURE')?.value || 0;
  const humidity = zone.sensors?.find(s => s.type === 'HUMIDITY')?.value || 0;
  const co2 = zone.sensors?.find(s => s.type === 'CO2')?.value || 0;
  const occupancy = zone.sensors?.find(s => s.type === 'OCCUPANCY')?.value || 0;

  // Get HVAC status
  const hvac = zone.hvac;
  const hvacMode = hvac?.mode || 'off';
  const hvacStatus = (hvac?.is_cooling || hvac?.is_heating) ? 'Active' : 'Standby';
  
  // Get camera stream URL from backend API
  const camera = zone.cameras?.[0];
  const streamUrl = camera?.hls_url || null;

  // Check for active alerts
  const hasAlerts = zone.active_alerts_count > 0;

  // Temperature status color
  const getTempColor = (temp) => {
    if (temp < 18) return 'text-blue-500';
    if (temp > 26) return 'text-red-500';
    return 'text-green-500';
  };

  // CO2 status color
  const getCO2Color = (co2) => {
    if (co2 > 1000) return 'text-red-500';
    if (co2 > 800) return 'text-yellow-500';
    return 'text-green-500';
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className={`p-4 ${hasAlerts ? 'bg-red-50 border-l-4 border-red-500' : 'bg-gray-50'}`}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-800">{zone.name}</h3>
            <p className="text-sm text-gray-600">Floor {zone.floor_number}</p>
          </div>
          {hasAlerts && (
            <div className="flex items-center text-red-600">
              <AlertTriangle className="w-5 h-5 mr-1" />
              <span className="text-sm font-medium">{zone.active_alerts_count} Alert{zone.active_alerts_count > 1 ? 's' : ''}</span>
            </div>
          )}
        </div>
      </div>

      {/* Sensor Data */}
      <div className="p-4 grid grid-cols-2 gap-3">
        {/* Temperature */}
        <div className="flex items-center gap-2">
          <Thermometer className={`w-5 h-5 ${getTempColor(temperature)}`} />
          <div>
            <p className="text-xs text-gray-500">Temperature</p>
            <p className={`text-lg font-semibold ${getTempColor(temperature)}`}>
              {temperature.toFixed(1)}°C
            </p>
          </div>
        </div>

        {/* Humidity */}
        <div className="flex items-center gap-2">
          <Droplets className="w-5 h-5 text-blue-500" />
          <div>
            <p className="text-xs text-gray-500">Humidity</p>
            <p className="text-lg font-semibold text-gray-800">
              {humidity.toFixed(0)}%
            </p>
          </div>
        </div>

        {/* CO2 */}
        <div className="flex items-center gap-2">
          <Wind className={`w-5 h-5 ${getCO2Color(co2)}`} />
          <div>
            <p className="text-xs text-gray-500">CO₂</p>
            <p className={`text-lg font-semibold ${getCO2Color(co2)}`}>
              {co2.toFixed(0)} ppm
            </p>
          </div>
        </div>

        {/* Occupancy */}
        <div className="flex items-center gap-2">
          <Users className="w-5 h-5 text-purple-500" />
          <div>
            <p className="text-xs text-gray-500">Occupancy</p>
            <p className="text-lg font-semibold text-gray-800">
              {occupancy} people
            </p>
          </div>
        </div>
      </div>

      {/* HVAC Status */}
      {hvac && (
        <div className="px-4 pb-3">
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-500">HVAC System</p>
                <p className="text-sm font-medium text-gray-800 capitalize">{hvac.mode_display || hvacMode}</p>
              </div>
              <div className="flex items-center gap-2">
                <span className={`text-xs font-medium ${(hvac.is_cooling || hvac.is_heating) ? 'text-green-600' : 'text-gray-500'}`}>
                  {hvac.status || hvacStatus}
                </span>
                {(hvac.is_cooling || hvac.is_heating) && (
                  <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                )}
              </div>
            </div>
            {hvac.set_temp && (
              <p className="text-xs text-gray-600 mt-1">
                Current: {hvac.current_temp}°C | Target: {hvac.set_temp}°C
              </p>
            )}
          </div>
        </div>
      )}

      {/* Camera Section */}
      {camera && (
        <div className="px-4 pb-4">
          <button
            onClick={() => setShowCamera(!showCamera)}
            className="w-full flex items-center justify-between p-3 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
          >
            <div className="flex items-center gap-2">
              <Video className="w-5 h-5 text-blue-600" />
              <span className="text-sm font-medium text-blue-800">
                {showCamera ? 'Hide' : 'Show'} Live Camera
              </span>
            </div>
            <span className="text-xs text-blue-600">{camera.name}</span>
          </button>

          {showCamera && streamUrl && (
            <div className="mt-3">
              <LiveCameraView
                streamUrl={streamUrl}
                title={camera.name}
                className="rounded-lg"
              />
            </div>
          )}
        </div>
      )}

      {/* View Details Button */}
      <div className="px-4 pb-4">
        <button
          onClick={() => onZoneClick && onZoneClick(zone)}
          className="w-full py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors text-sm font-medium"
        >
          View Details
        </button>
      </div>
    </div>
  );
};

export default ZoneCard;
