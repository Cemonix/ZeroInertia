# Monitoring Setup Guide

Complete step-by-step guide to set up monitoring for Zero Inertia.

## Table of Contents

- [Quick Start (5 Minutes)](#quick-start-5-minutes)
- [Detailed Setup](#detailed-setup)
- [Accessing Monitoring Services](#accessing-monitoring-services)
- [Security Configuration](#security-configuration)
- [Umami Analytics Setup](#umami-analytics-setup)
- [Troubleshooting](#troubleshooting)
- [Useful Commands](#useful-commands)

## Quick Start (5 Minutes)

### 1. Install Backend Dependency

```bash
cd backend
poetry add prometheus-fastapi-instrumentator
```

### 2. Configure Environment Variables

Create/edit your `.env` file in the project root:

```bash
# Grafana Configuration
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=your_secure_password_here
GRAFANA_DOMAIN=zeroinertia.cemonix.dev

# Umami Analytics
UMAMI_DB_NAME=umami
UMAMI_DB_USER=umami
UMAMI_DB_PASSWORD=your_secure_password_here
UMAMI_APP_SECRET=$(openssl rand -hex 32)  # Generate random secret
```

**⚠️ Security Note:** Replace all `your_secure_password_here` with strong passwords!

### 3. Generate Basic Auth Password

The monitoring endpoints are protected with HTTP basic authentication:

```bash
# Generate a secure password
NEW_PASSWORD=$(openssl rand -base64 16)
echo "Your basic auth password: $NEW_PASSWORD"
echo "Save this securely!"

# Start Caddy to generate hash
docker-compose -f docker-compose.prod.yml up -d caddy

# Generate password hash
docker exec -it zero_inertia_caddy caddy hash-password --plaintext "$NEW_PASSWORD"
```

Copy the hash (starts with `$2a$14$...`) and update the `Caddyfile`.

### 4. Update Caddyfile

Edit the root `Caddyfile` and add the hash to all `basicauth` blocks:

```
basicauth {
    # Username: admin
    # Password: <your password from step 3>
    admin $2a$14$YOUR_HASH_HERE
}
```

### 5. Start Monitoring Stack

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Verify all services are running
docker-compose -f docker-compose.prod.yml ps
```

All services should show status "Up".

## Detailed Setup

### Step 1: Backend Instrumentation

The backend is already instrumented with Prometheus metrics. Verify the configuration:

**File:** `backend/app/main.py`

```python
from prometheus_fastapi_instrumentator import Instrumentator

# Auto-instrumentation for HTTP metrics
if settings.environment == "production":
    Instrumentator().instrument(app).expose(app)
```

This automatically exposes metrics at:
- `http://backend:8000/metrics` - Standard HTTP metrics
- `http://backend:8000/api/v1/metrics/business-metrics` - Custom business metrics

### Step 2: Prometheus Configuration

**File:** `prometheus.yml`

The configuration defines scrape targets:

```yaml
scrape_configs:
  # Backend API metrics
  - job_name: 'fastapi'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['backend:8000']

  # Custom business metrics
  - job_name: 'business_metrics'
    scrape_interval: 30s
    metrics_path: '/api/v1/metrics/business-metrics'
    static_configs:
      - targets: ['backend:8000']

  # System metrics
  - job_name: 'node_exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  # Prometheus self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
```

No changes needed unless you want to customize scrape intervals.

### Step 3: Grafana Provisioning

Grafana is configured to automatically load:
- **Datasource**: Prometheus connection
- **Dashboards**: Zero Inertia overview dashboard

**Files:**
- `grafana/provisioning/datasources/prometheus.yml` - Datasource config
- `grafana/provisioning/dashboards/dashboards.yml` - Dashboard provisioning
- `grafana/dashboards/zero-inertia-overview.json` - Dashboard definition

These are automatically loaded when Grafana starts.

### Step 4: Docker Compose Configuration

**File:** `docker-compose.prod.yml`

Key configurations:

**Prometheus:**
```yaml
prometheus:
  image: prom/prometheus:latest
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'
    - '--storage.tsdb.retention.time=7d'
    - '--web.external-url=https://zeroinertia.cemonix.dev/prometheus'
    - '--web.route-prefix=/prometheus'  # Important: matches the subpath
```

**Grafana:**
```yaml
grafana:
  image: grafana/grafana:latest
  environment:
    - GF_SERVER_ROOT_URL=%(protocol)s://%(domain)s/grafana/
    - GF_SERVER_SERVE_FROM_SUB_PATH=true
    - GF_SECURITY_ADMIN_USER=${GRAFANA_ADMIN_USER:-admin}
    - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:-admin}
```

**Umami:**
```yaml
umami:
  image: ghcr.io/umami-software/umami:postgresql-latest
  environment:
    DATABASE_URL: postgresql://${UMAMI_DB_USER}:${UMAMI_DB_PASSWORD}@umami-db:5432/${UMAMI_DB_NAME}
    APP_SECRET: ${UMAMI_APP_SECRET}
    APP_URL: https://zeroinertia.cemonix.dev/umami
    BASE_PATH: /umami  # Important: serves from subpath
```

## Accessing Monitoring Services

### Service URLs

All monitoring services are accessible through your main domain with subpaths:

| Service | URL | Authentication |
|---------|-----|----------------|
| **Grafana** | `https://zeroinertia.cemonix.dev/grafana` | Basic auth → Grafana login |
| **Prometheus** | `https://zeroinertia.cemonix.dev/prometheus` | Basic auth only |
| **Umami** | `https://zeroinertia.cemonix.dev/umami` | Basic auth → Umami login |

### Authentication Layers

#### Layer 1: Basic Authentication (Caddy)

All monitoring endpoints require basic auth credentials:

- **Username**: `admin` (configurable in Caddyfile)
- **Password**: Set during setup (step 3 above)

This is configured in the `Caddyfile`:

```
handle_path /grafana* {
    basicauth {
        admin $2a$14$YOUR_HASH_HERE
    }
    reverse_proxy grafana:3000
}
```

#### Layer 2: Service-Specific Login

**Grafana:**
- After basic auth, Grafana's login page appears
- Username: `admin` (or `GRAFANA_ADMIN_USER`)
- Password: Set via `GRAFANA_ADMIN_PASSWORD` env variable

**Umami:**
- After basic auth, Umami's login page appears
- First visit: Create admin account
- Subsequent visits: Use your Umami credentials

**Prometheus:**
- No additional authentication
- Protected only by basic auth layer

## Security Configuration

### Change Default Passwords

**⚠️ CRITICAL: Change these before production deployment!**

#### 1. Basic Auth Password (Caddy)

Already done in Quick Start step 3-4. To change later:

```bash
# Generate new password
NEW_PASSWORD="your-new-password"

# Generate hash
docker exec -it zero_inertia_caddy caddy hash-password --plaintext "$NEW_PASSWORD"

# Update Caddyfile with new hash
# Then reload Caddy
docker exec -it zero_inertia_caddy caddy reload --config /etc/caddy/Caddyfile
```

#### 2. Grafana Admin Password

Edit your `.env` file:

```bash
GRAFANA_ADMIN_PASSWORD=your_new_secure_password
```

Then restart Grafana:

```bash
docker-compose -f docker-compose.prod.yml restart grafana
```

#### 3. Umami Password

Change from the Umami web interface:
1. Log in to Umami
2. Go to Settings → Profile
3. Change password

### Optional: IP Restriction

Restrict monitoring access to specific IPs by editing `Caddyfile`:

```
handle_path /grafana* {
    @allowed {
        remote_ip 192.168.1.0/24 10.0.0.0/8  # Your trusted IPs
    }
    basicauth @allowed {
        admin $2a$14$YOUR_HASH_HERE
    }
    reverse_proxy grafana:3000
}
```

### Enable Grafana Audit Logging

For compliance tracking, enable audit logs in `docker-compose.prod.yml`:

```yaml
grafana:
  environment:
    - GF_LOG_LEVEL=info
    - GF_SECURITY_AUDIT_ENABLED=true
  volumes:
    - ./grafana/logs:/var/log/grafana
```

## Umami Analytics Setup

### Initial Configuration

1. **Access Umami**: Navigate to `https://zeroinertia.cemonix.dev/umami`

2. **Create Admin Account** (first visit only):
   - Email: your-email@example.com
   - Username: admin
   - Password: (choose a strong password)

3. **Add Website**:
   - Click "Add Website"
   - **Name**: Zero Inertia
   - **Domain**: `zeroinertia.cemonix.dev` (your actual domain)
   - **Enable Share URL**: No (keep private)
   - Click "Save"

4. **Get Tracking Code**:
   - Click on your website name
   - Go to "Settings" tab
   - Copy the **Website ID** (UUID format)
   - Note the **script URL**

### Frontend Integration

**Option 1: Add to index.html (Recommended)**

Edit `frontend/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <!-- ... other head content ... -->

    <!-- Umami Analytics -->
    <script
      defer
      src="https://zeroinertia.cemonix.dev/umami/script.js"
      data-website-id="YOUR_WEBSITE_ID_HERE">
    </script>
  </head>
  <body>
    <!-- ... -->
  </body>
</html>
```

**Option 2: Add via environment variable**

Create `frontend/.env.production`:

```bash
VITE_UMAMI_WEBSITE_ID=your_website_id_here
VITE_UMAMI_SRC=https://zeroinertia.cemonix.dev/umami/script.js
```

Then add to `frontend/src/main.ts`:

```typescript
// Umami analytics
if (import.meta.env.VITE_UMAMI_WEBSITE_ID) {
  const script = document.createElement('script');
  script.defer = true;
  script.src = import.meta.env.VITE_UMAMI_SRC;
  script.setAttribute('data-website-id', import.meta.env.VITE_UMAMI_WEBSITE_ID);
  document.head.appendChild(script);
}
```

### Rebuild and Deploy

After adding the tracking code:

```bash
# Rebuild frontend
cd frontend
npm run build

# Restart frontend container
cd ..
docker-compose -f docker-compose.prod.yml restart frontend
```

### Verify Tracking

1. Visit your website in an incognito window
2. Navigate to a few pages
3. Check Umami dashboard - you should see page views within 30 seconds

## Troubleshooting

### Metrics Not Appearing in Grafana

**Problem**: Grafana dashboard is empty or showing "No data"

**Solution**:

1. **Check Prometheus is scraping**:
   ```bash
   # Open Prometheus targets page
   open https://zeroinertia.cemonix.dev/prometheus/targets

   # All targets should show "UP" status
   ```

2. **Verify backend metrics endpoint**:
   ```bash
   # Check if metrics are exposed
   curl http://localhost:8000/metrics
   curl http://localhost:8000/api/v1/metrics/business-metrics

   # Should return metrics in Prometheus format
   ```

3. **Check Prometheus logs**:
   ```bash
   docker logs zero_inertia_prometheus | grep -i error
   ```

4. **Verify datasource in Grafana**:
   - Login to Grafana
   - Configuration → Data sources
   - Click "Prometheus"
   - Click "Save & test" - should show green "Data source is working"

### Grafana Shows 404 or Asset Errors

**Problem**: Grafana loads but CSS/JS fail to load, or shows 404

**Solution**:

1. **Verify subpath configuration**:
   ```bash
   docker logs zero_inertia_grafana | grep -i "server root"
   ```
   Should show: `root_url=https://zeroinertia.cemonix.dev/grafana/`

2. **Check environment variables**:
   ```yaml
   GF_SERVER_ROOT_URL=%(protocol)s://%(domain)s/grafana/  # Note trailing slash!
   GF_SERVER_SERVE_FROM_SUB_PATH=true
   ```

3. **Restart Grafana**:
   ```bash
   docker-compose -f docker-compose.prod.yml restart grafana
   ```

### Prometheus Shows Wrong Base URL

**Problem**: Links in Prometheus UI point to wrong URLs

**Solution**:

Verify the `--web.external-url` flag in `docker-compose.prod.yml`:

```yaml
command:
  - '--web.external-url=https://zeroinertia.cemonix.dev/prometheus'
  - '--web.route-prefix=/prometheus'  # Must match the subpath
```

Restart Prometheus:
```bash
docker-compose -f docker-compose.prod.yml restart prometheus
```

### Umami Not Tracking Page Views

**Problem**: No analytics data appearing in Umami

**Solution**:

1. **Check browser console**:
   - Open DevTools → Console
   - Look for `/umami/script.js` loaded
   - No CORS or 404 errors

2. **Verify Website ID**:
   - Ensure UUID in script tag matches Umami dashboard

3. **Check Umami logs**:
   ```bash
   docker logs zero_inertia_umami
   ```

4. **Verify database connection**:
   ```bash
   docker logs zero_inertia_umami_db
   docker exec -it zero_inertia_umami_db pg_isready -U umami
   ```

5. **Test with curl**:
   ```bash
   # Should return JavaScript code
   curl https://zeroinertia.cemonix.dev/umami/script.js
   ```

### Basic Auth Not Working

**Problem**: Basic auth prompt doesn't appear or credentials rejected

**Solution**:

1. **Validate Caddyfile**:
   ```bash
   docker exec -it zero_inertia_caddy caddy validate --config /etc/caddy/Caddyfile
   ```

2. **Check Caddy logs**:
   ```bash
   docker logs zero_inertia_caddy | tail -50
   ```

3. **Regenerate password hash**:
   ```bash
   # Make sure you're using the correct password
   docker exec -it zero_inertia_caddy caddy hash-password --plaintext 'your-password'
   ```

4. **Reload Caddy configuration**:
   ```bash
   docker exec -it zero_inertia_caddy caddy reload --config /etc/caddy/Caddyfile
   ```

### Services Not Starting

**Problem**: Monitoring containers fail to start

**Solution**:

1. **Check all containers**:
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   ```

2. **View logs for failed service**:
   ```bash
   docker logs zero_inertia_prometheus
   docker logs zero_inertia_grafana
   docker logs zero_inertia_umami
   ```

3. **Check disk space**:
   ```bash
   df -h
   # Ensure you have at least 2GB free
   ```

4. **Verify configuration files**:
   ```bash
   # Prometheus config
   docker exec zero_inertia_prometheus promtool check config /etc/prometheus/prometheus.yml
   ```

### High Disk Usage

**Problem**: Monitoring is consuming too much disk space

**Solution**:

1. **Check current usage**:
   ```bash
   # Prometheus data
   docker exec zero_inertia_prometheus du -sh /prometheus

   # Grafana data
   docker exec zero_inertia_grafana du -sh /var/lib/grafana
   ```

2. **Reduce Prometheus retention**:

   Edit `docker-compose.prod.yml`:
   ```yaml
   command:
     - '--storage.tsdb.retention.time=3d'  # Reduce from 7d to 3d
   ```

   Restart Prometheus:
   ```bash
   docker-compose -f docker-compose.prod.yml restart prometheus
   ```

3. **Clean old data** (⚠️ loses historical data):
   ```bash
   # Stop Prometheus
   docker-compose -f docker-compose.prod.yml stop prometheus

   # Remove old data
   docker exec zero_inertia_prometheus rm -rf /prometheus/*

   # Restart
   docker-compose -f docker-compose.prod.yml start prometheus
   ```

## Useful Commands

### Service Management

```bash
# Start all monitoring services
docker-compose -f docker-compose.prod.yml up -d prometheus grafana node-exporter umami umami-db

# Stop monitoring services
docker-compose -f docker-compose.prod.yml stop prometheus grafana node-exporter umami

# Restart specific service
docker-compose -f docker-compose.prod.yml restart grafana

# View logs (follow mode)
docker-compose -f docker-compose.prod.yml logs -f prometheus grafana umami

# Check service status
docker-compose -f docker-compose.prod.yml ps
```

### Metrics Queries

```bash
# View backend metrics
curl http://localhost:8000/metrics

# View business metrics
curl http://localhost:8000/api/v1/metrics/business-metrics

# Query Prometheus API
curl 'http://localhost:9090/api/v1/query?query=zero_inertia_total_users'

# Query with time range
curl 'http://localhost:9090/api/v1/query_range?query=http_requests_total&start=2024-01-01T00:00:00Z&end=2024-01-02T00:00:00Z&step=15s'
```

### Configuration Validation

```bash
# Validate Prometheus config
docker exec zero_inertia_prometheus promtool check config /etc/prometheus/prometheus.yml

# Validate Caddyfile
docker exec -it zero_inertia_caddy caddy validate --config /etc/caddy/Caddyfile

# Check Grafana provisioning
docker logs zero_inertia_grafana | grep -i provision
```

### Backup & Restore

```bash
# Backup Grafana dashboards
docker exec zero_inertia_grafana tar czf /tmp/grafana-backup.tar.gz /var/lib/grafana
docker cp zero_inertia_grafana:/tmp/grafana-backup.tar.gz ./grafana-backup.tar.gz

# Backup Prometheus data (optional, usually not needed)
docker exec zero_inertia_prometheus tar czf /tmp/prometheus-backup.tar.gz /prometheus
docker cp zero_inertia_prometheus:/tmp/prometheus-backup.tar.gz ./prometheus-backup.tar.gz

# Backup Umami database
docker exec zero_inertia_umami_db pg_dump -U umami umami > umami-backup.sql
```

### Debugging

```bash
# Enter Grafana container
docker exec -it zero_inertia_grafana sh

# Enter Prometheus container
docker exec -it zero_inertia_prometheus sh

# Check network connectivity
docker exec zero_inertia_prometheus wget -O- http://backend:8000/metrics

# View Prometheus targets from CLI
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets'
```

## Next Steps

1. **Explore Grafana**: Create custom dashboards for your specific needs
2. **Set up Alerts**: Configure notification channels (email, Slack, etc.)
3. **Review Metrics**: Check the [overview.md](./overview.md) for all available metrics
4. **Optimize**: Fine-tune scrape intervals and retention based on your usage

---

**Need help?** Check the [Troubleshooting](#troubleshooting) section or refer to the [overview.md](./overview.md) for architectural details.
