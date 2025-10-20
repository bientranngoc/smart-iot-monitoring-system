# 🚀 Complete Setup Instructions

## Step-by-Step Guide to Run React Dashboard

### 1️⃣ Install Node.js (if not installed)

Download and install Node.js from: https://nodejs.org/
- Choose LTS version (18.x or higher)
- Verify installation:

```powershell
node --version
npm --version
```

### 2️⃣ Install Frontend Dependencies

```powershell
# Navigate to frontend folder
cd D:\job\smart-iot-monitoring-system\frontend

# Install all packages
npm install
```

This will install:
- React 18.2.0
- Vite 5.0.0
- Tailwind CSS 3.3.0
- Recharts 2.10.0
- Axios 1.6.0
- React Router 6.20.0

### 3️⃣ Configure Django CORS

```powershell
# Install django-cors-headers in Docker container
docker exec -it iot-app pip install django-cors-headers
```

Update `smart_iot/settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',  # Add this
    'monitoring',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Add this at the top
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Add CORS configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

Restart Django:
```powershell
docker restart iot-app
```

### 4️⃣ Start Frontend Development Server

```powershell
# In frontend folder
npm run dev
```

You should see:
```
  VITE v5.0.0  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

### 5️⃣ Open Dashboard

Open browser and navigate to: **http://localhost:3000**

### 6️⃣ Verify Everything Works

Check these pages:
1. **Dashboard (/)** - Should show stats, charts, latest readings
2. **Devices (/devices)** - Should list all devices
3. **Readings (/readings)** - Should show table of readings
4. **Search (/search)** - Should allow advanced search

---

## 🔧 Troubleshooting

### Problem: `npm: command not found`
**Solution**: Install Node.js from https://nodejs.org/

### Problem: CORS error in browser console
**Solution**: 
1. Check django-cors-headers is installed
2. Verify CORS_ALLOWED_ORIGINS in settings.py
3. Restart Django: `docker restart iot-app`

### Problem: API returns 404
**Solution**: 
1. Check Django is running: `docker ps`
2. Verify API endpoints: `curl http://localhost:8000/api/readings/`

### Problem: Charts not rendering
**Solution**: 
1. Check recharts is installed: `npm list recharts`
2. If not: `npm install recharts`

### Problem: Styles look broken
**Solution**: 
1. Check Tailwind is in package.json
2. Restart dev server: `Ctrl+C` then `npm run dev`

---

## 📊 Expected Results

### Dashboard
- 4 stats cards with numbers
- Latest readings table (updates every 5s)
- 5 interactive charts
- Gradient colors and animations

### Devices
- List of devices on left
- Click device to see details on right
- Table of 50 recent readings

### Readings
- Filterable table
- Export CSV button works
- Color-coded temperature/humidity

### Search
- Search form with examples
- Fast results (<50ms)
- Device and time filters work

---

## 🎉 You're Done!

Your complete IoT monitoring system is now running:

**Backend (Django + MongoDB + OpenSearch)**: http://localhost:8000
**Frontend (React Dashboard)**: http://localhost:3000

Enjoy! 🚀🌡️📊
