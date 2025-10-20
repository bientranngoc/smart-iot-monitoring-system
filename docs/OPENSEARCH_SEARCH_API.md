# OpenSearch Search API Documentation

## 🔍 Endpoint: Search Readings

**URL:** `GET /api/readings/search/`

This endpoint allows you to search sensor readings using OpenSearch with powerful query capabilities.

---

## 📋 Query Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `q` | string | Search query with field-specific filters | `temperature:>25` |
| `device_id` | integer | Filter by specific device | `1` |
| `from_date` | ISO datetime | Start date/time | `2025-10-20T00:00:00Z` |
| `to_date` | ISO datetime | End date/time | `2025-10-20T23:59:59Z` |
| `range` | string | Time range shortcut (`1h`, `24h`, `7d`) | `24h` |
| `limit` | integer | Max results (default: 100) | `50` |

---

## 🎯 Query Syntax

### 1. Field-specific queries

**Temperature greater than 25:**
```
GET /api/readings/search/?q=temperature:>25
```

**Humidity less than 60:**
```
GET /api/readings/search/?q=humidity:<60
```

**Temperature equals 25:**
```
GET /api/readings/search/?q=temperature:=25
```

### 2. Device filter

**Get readings from device 1:**
```
GET /api/readings/search/?device_id=1
```

### 3. Date range

**Readings between specific dates:**
```
GET /api/readings/search/?from_date=2025-10-20T00:00:00Z&to_date=2025-10-20T23:59:59Z
```

### 4. Time range shortcuts

**Last 1 hour:**
```
GET /api/readings/search/?range=1h
```

**Last 24 hours:**
```
GET /api/readings/search/?range=24h
```

**Last 7 days:**
```
GET /api/readings/search/?range=7d
```

### 5. Combined queries

**Device 1, temperature > 25, last 24 hours:**
```
GET /api/readings/search/?device_id=1&q=temperature:>25&range=24h
```

**Device 2, humidity < 60, limit to 10 results:**
```
GET /api/readings/search/?device_id=2&q=humidity:<60&limit=10
```

---

## 📊 Response Format

```json
{
  "total": 26,
  "results": [
    {
      "device_id": 1,
      "temperature": 26.0,
      "humidity": 59.64,
      "timestamp": "2025-10-20T07:01:12.498000"
    },
    {
      "device_id": 2,
      "temperature": 27.9,
      "humidity": 61.7,
      "timestamp": "2025-10-20T07:01:10.497000"
    }
  ],
  "took_ms": 43
}
```

**Fields:**
- `total` - Total number of matching documents
- `results` - Array of reading objects
- `took_ms` - Query execution time in milliseconds

---

## 💡 Examples with curl

### Example 1: High temperature alerts
```powershell
curl "http://localhost:8000/api/readings/search/?q=temperature:>30"
```

### Example 2: Recent readings for device
```powershell
curl "http://localhost:8000/api/readings/search/?device_id=1&range=1h"
```

### Example 3: Low humidity warnings
```powershell
curl "http://localhost:8000/api/readings/search/?q=humidity:<40&limit=20"
```

### Example 4: Specific date range
```powershell
curl "http://localhost:8000/api/readings/search/?from_date=2025-10-20T00:00:00Z&to_date=2025-10-20T12:00:00Z"
```

### Example 5: Complex query
```powershell
curl "http://localhost:8000/api/readings/search/?device_id=2&q=temperature:>25&range=24h&limit=50"
```

---

## 🆚 Comparison with MongoDB API

| Feature | MongoDB API (`/api/readings/`) | OpenSearch API (`/api/readings/search/`) |
|---------|-------------------------------|------------------------------------------|
| **Speed** | Good for recent data | ⚡ Faster for complex queries |
| **Query** | Simple filters | 🔍 Advanced search (>, <, =) |
| **Range** | Time-based only | Time + field-based |
| **Full-text** | ❌ Not supported | ✅ Supported |
| **Aggregation** | Limited | Advanced |
| **Best for** | Latest readings | Historical analysis, alerts |

---

## 🎓 Use Cases

### 1. Temperature Alerts
Monitor devices with temperature above threshold:
```
/api/readings/search/?q=temperature:>30&range=1h
```

### 2. Anomaly Detection
Find readings with unusual humidity:
```
/api/readings/search/?q=humidity:<30
/api/readings/search/?q=humidity:>90
```

### 3. Device Performance
Analyze specific device over time:
```
/api/readings/search/?device_id=1&range=24h&limit=1000
```

### 4. Data Export
Get all readings for a specific period:
```
/api/readings/search/?from_date=2025-10-01T00:00:00Z&to_date=2025-10-31T23:59:59Z&limit=10000
```

---

## 🚀 Performance Tips

1. **Use `limit` wisely** - Default is 100, don't fetch more than needed
2. **Narrow time range** - Use `range` or `from_date/to_date` to reduce search scope
3. **Device filter first** - If querying specific device, always include `device_id`
4. **Check `took_ms`** - Monitor query performance in response

---

## ⚠️ Error Handling

**OpenSearch not available:**
```json
{
  "error": "OpenSearch error: Connection refused"
}
```
Status: 500

**Invalid query:**
Returns empty results with `total: 0`

---

## 🔗 Related Endpoints

- `GET /api/readings/` - List recent readings (MongoDB)
- `GET /api/readings/latest_all/` - Get latest from Redis cache
- `GET /api/readings/stats/` - Get statistics
- `GET /api/devices/{id}/readings/` - Device-specific readings

---

## 📝 Summary

The `/api/readings/search/` endpoint provides powerful search capabilities using OpenSearch:

✅ **Field-specific queries** (`temperature:>25`)
✅ **Device filtering** (`device_id=1`)  
✅ **Date range filtering** (`from_date`, `to_date`)
✅ **Time shortcuts** (`1h`, `24h`, `7d`)
✅ **Fast performance** (millisecond response times)
✅ **Flexible limits** (customize result size)

**Perfect for:**
- 🔔 Alert systems
- 📊 Analytics dashboards
- 📈 Historical analysis
- 🔍 Data exploration
