# OpenSearch Aggregations API Documentation

## 📊 Endpoint: Statistical Aggregations

**URL:** `GET /api/readings/aggregations/`

This endpoint provides statistical aggregations (avg, min, max, count) for temperature and humidity data using OpenSearch.

---

## 📋 Query Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `device_id` | integer | Filter by specific device (optional) | `1` |
| `range` | string | Time range (`1h`, `24h`, `7d`) | `24h` |

---

## 📊 Response Format

```json
{
  "total_documents": 41,
  "temperature": {
    "avg": 25.24,
    "min": 20.63,
    "max": 29.72,
    "count": 41
  },
  "humidity": {
    "avg": 58.18,
    "min": 50.59,
    "max": 69.24,
    "count": 41
  },
  "by_device": [
    {
      "device_id": 1,
      "count": 7,
      "avg_temperature": 24.78,
      "avg_humidity": 58.85
    },
    {
      "device_id": 2,
      "count": 9,
      "avg_temperature": 25.67,
      "avg_humidity": 59.12
    }
  ],
  "temperature_distribution": [
    {
      "range": "20-25°C",
      "count": 18
    },
    {
      "range": "25-30°C",
      "count": 23
    }
  ],
  "query_time_ms": 12
}
```

---

## 💡 Response Fields

### Overall Statistics

- **`total_documents`** - Total number of readings analyzed
- **`query_time_ms`** - Query execution time in milliseconds

### Temperature Stats

- **`temperature.avg`** - Average temperature (°C)
- **`temperature.min`** - Minimum temperature (°C)
- **`temperature.max`** - Maximum temperature (°C)
- **`temperature.count`** - Number of temperature readings

### Humidity Stats

- **`humidity.avg`** - Average humidity (%)
- **`humidity.min`** - Minimum humidity (%)
- **`humidity.max`** - Maximum humidity (%)
- **`humidity.count`** - Number of humidity readings

### By Device

Array of statistics per device:
- **`device_id`** - Device identifier
- **`count`** - Number of readings from this device
- **`avg_temperature`** - Average temperature for this device
- **`avg_humidity`** - Average humidity for this device

### Temperature Distribution

Histogram showing temperature ranges:
- **`range`** - Temperature range (5°C intervals)
- **`count`** - Number of readings in this range

---

## 🎯 Examples

### Example 1: Overall Statistics
Get statistics for all devices and all time:

```powershell
curl "http://localhost:8000/api/readings/aggregations/"
```

**Response:**
```json
{
  "total_documents": 41,
  "temperature": {
    "avg": 25.24,
    "min": 20.63,
    "max": 29.72,
    "count": 41
  },
  "humidity": {
    "avg": 58.18,
    "min": 50.59,
    "max": 69.24,
    "count": 41
  },
  "by_device": [...],
  "temperature_distribution": [...],
  "query_time_ms": 12
}
```

### Example 2: Device-Specific Statistics
Get statistics for device 1 only:

```powershell
curl "http://localhost:8000/api/readings/aggregations/?device_id=1"
```

**Response:**
```json
{
  "total_documents": 7,
  "temperature": {
    "avg": 24.78,
    "min": 20.63,
    "max": 26.79,
    "count": 7
  },
  "humidity": {
    "avg": 58.85,
    "min": 55.03,
    "max": 66.35,
    "count": 7
  },
  "by_device": [
    {
      "device_id": 1,
      "count": 7,
      "avg_temperature": 24.78,
      "avg_humidity": 58.85
    }
  ],
  "query_time_ms": 8
}
```

### Example 3: Last 24 Hours Statistics
Get statistics for the last 24 hours:

```powershell
curl "http://localhost:8000/api/readings/aggregations/?range=24h"
```

### Example 4: Device Statistics for Last Hour
Combine device filter with time range:

```powershell
curl "http://localhost:8000/api/readings/aggregations/?device_id=2&range=1h"
```

---

## 🆚 Comparison with MongoDB Stats

| Feature | MongoDB Stats (`/api/readings/stats/`) | OpenSearch Aggs (`/api/readings/aggregations/`) |
|---------|---------------------------------------|------------------------------------------------|
| **Data Source** | MongoDB | OpenSearch |
| **Speed** | Good | ⚡ Faster for large datasets |
| **Aggregations** | Basic count | Advanced (avg, min, max, histogram) |
| **Time Range** | ❌ Not supported | ✅ Supported (1h, 24h, 7d) |
| **Per-Device Stats** | Count only | Full statistics |
| **Distribution** | ❌ Not available | ✅ Temperature histogram |
| **Best For** | Quick counts | Detailed analytics |

---

## 📈 Use Cases

### 1. Dashboard Overview
Get overall statistics for display on dashboard:
```
GET /api/readings/aggregations/
```
Display: Total readings, avg/min/max temperature and humidity

### 2. Device Performance Monitoring
Monitor specific device performance:
```
GET /api/readings/aggregations/?device_id=1&range=24h
```
Display: 24-hour statistics for device 1

### 3. Temperature Distribution Analysis
Analyze temperature patterns across all devices:
```
GET /api/readings/aggregations/
```
Use `temperature_distribution` field for histogram chart

### 4. Comparative Analysis
Compare statistics across devices:
```
GET /api/readings/aggregations/?range=7d
```
Use `by_device` field to compare average values

### 5. Alert Thresholds
Determine appropriate alert thresholds:
```
GET /api/readings/aggregations/
```
Use `max` and `min` values to set realistic thresholds

---

## 🎨 Frontend Integration Examples

### JavaScript (Chart.js)
```javascript
fetch('http://localhost:8000/api/readings/aggregations/')
  .then(response => response.json())
  .then(data => {
    // Temperature distribution chart
    const labels = data.temperature_distribution.map(d => d.range);
    const values = data.temperature_distribution.map(d => d.count);
    
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Temperature Distribution',
          data: values
        }]
      }
    });
  });
```

### Python (Data Analysis)
```python
import requests
import pandas as pd

response = requests.get('http://localhost:8000/api/readings/aggregations/')
data = response.json()

# Create DataFrame for device comparison
df = pd.DataFrame(data['by_device'])
print(df)

# Output:
#    device_id  count  avg_temperature  avg_humidity
# 0          1      7            24.78         58.85
# 1          2      9            25.67         59.12
```

---

## 🚀 Performance Tips

1. **Use time ranges** - Narrow the dataset with `range` parameter
2. **Device-specific queries** - Filter by `device_id` for faster results
3. **Monitor query_time_ms** - Track performance in response
4. **Cache results** - Consider caching aggregations for frequently accessed data

---

## ⚠️ Notes

- All numeric values are rounded to 2 decimal places
- `null` values returned when no data available
- Temperature distribution uses 5°C intervals
- Query time typically < 50ms for thousands of documents

---

## 🔗 Related Endpoints

- `GET /api/readings/stats/` - Basic MongoDB statistics (count only)
- `GET /api/readings/search/` - Advanced search with filters
- `GET /api/readings/` - List recent readings
- `GET /api/devices/{id}/readings/` - Device-specific readings history

---

## 📝 Summary

The `/api/readings/aggregations/` endpoint provides:

✅ **Statistical analysis** (avg, min, max, count)
✅ **Per-device breakdown** (compare devices)
✅ **Temperature distribution** (histogram data)
✅ **Time range filtering** (1h, 24h, 7d)
✅ **Fast performance** (< 50ms typical)
✅ **Rich data** for charts and dashboards

**Perfect for:**
- 📊 Analytics dashboards
- 📈 Performance monitoring
- 🔔 Alert threshold determination
- 📉 Trend analysis
- 🎯 Comparative studies
