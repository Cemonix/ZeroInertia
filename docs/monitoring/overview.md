# Monitoring Stack Overview

Comprehensive monitoring and analytics for Zero Inertia using Prometheus, Grafana, and Umami.

## Table of Contents

- [Architecture](#architecture)
- [Components](#components)
- [Available Metrics](#available-metrics)
- [Grafana Dashboards](#grafana-dashboards)
- [Best Practices](#best-practices)
- [Privacy & Compliance](#privacy--compliance)
- [Scaling Considerations](#scaling-considerations)

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Backend   │────▶│  Prometheus  │────▶│   Grafana   │
│  (FastAPI)  │     │   (Metrics)  │     │ (Dashboards)│
└─────────────┘     └──────────────┘     └─────────────┘
                            ▲
                            │
                    ┌───────┴─────────┐
                    │ Node Exporter   │
                    │ (System Metrics)│
                    └─────────────────┘

┌─────────────┐     ┌──────────────┐
│  Frontend   │────▶│    Umami     │
│   (Vue.js)  │     │ (Analytics)  │
└─────────────┘     └──────────────┘
```

### Traffic Flow

1. **Application Metrics**: FastAPI automatically exposes metrics at `/metrics`
2. **Business Metrics**: Custom endpoint at `/api/v1/metrics/business-metrics`
3. **Prometheus**: Scrapes metrics every 15 seconds (configurable)
4. **Grafana**: Queries Prometheus and displays visualizations
5. **Umami**: JavaScript tracker sends anonymous analytics data
6. **Caddy**: Reverse proxy with basic auth protecting monitoring endpoints

## Components

### Prometheus (Metrics Storage)
- **Purpose**: Time-series database for metrics
- **Port**: 9090 (internal)
- **URL**: `https://your-domain/prometheus` (basic auth protected)
- **Retention**: 7 days (~500MB disk usage)
- **Scrape Interval**: 15 seconds

### Grafana (Visualization)
- **Purpose**: Metrics dashboards and alerting
- **Port**: 3000 (internal)
- **URL**: `https://your-domain/grafana` (basic auth + Grafana login)
- **Default Login**: `admin` / (set via `GRAFANA_ADMIN_PASSWORD`)
- **Storage**: SQLite (~50MB)

### Node Exporter (System Metrics)
- **Purpose**: Server hardware and OS metrics
- **Port**: 9100 (internal)
- **Metrics**: CPU, memory, disk, network, filesystem

### Umami (Web Analytics)
- **Purpose**: Privacy-first website analytics
- **Port**: 3000 (internal)
- **URL**: `https://your-domain/umami` (basic auth + Umami login)
- **Database**: PostgreSQL (~100MB, grows with traffic)
- **Privacy**: No cookies, no PII, GDPR compliant

## Available Metrics

### Backend Metrics (Auto-instrumented)

Exposed at `http://backend:8000/metrics`:

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total HTTP requests by method and endpoint |
| `http_request_duration_seconds` | Histogram | Request latency distribution (p50, p95, p99) |
| `http_requests_in_progress` | Gauge | Current active requests |
| `http_request_size_bytes` | Summary | Request payload sizes |
| `http_response_size_bytes` | Summary | Response payload sizes |

### Business Metrics (Custom)

Exposed at `http://backend:8000/api/v1/metrics/business-metrics`:

| Metric | Type | Description |
|--------|------|-------------|
| `zero_inertia_total_users` | Gauge | Total registered users |
| `zero_inertia_active_users_7d` | Gauge | Users active in last 7 days |
| `zero_inertia_active_users_30d` | Gauge | Users active in last 30 days |
| `zero_inertia_total_tasks` | Gauge | Total tasks (not archived) |
| `zero_inertia_completed_tasks` | Gauge | Total completed tasks |
| `zero_inertia_total_projects` | Gauge | Total projects |
| `zero_inertia_total_notes` | Gauge | Total notes in knowledge hub |
| `zero_inertia_total_media` | Gauge | Total media items tracked (books, games, movies, etc.) |
| `zero_inertia_disk_usage_bytes` | Gauge | Current disk usage in bytes |
| `zero_inertia_disk_free_bytes` | Gauge | Free disk space in bytes |

### System Metrics (Node Exporter)

Exposed at `http://node-exporter:9100/metrics`:

- **CPU**: Usage per core, load average (1m, 5m, 15m)
- **Memory**: Total, free, cached, buffers, swap
- **Disk I/O**: Read/write operations, throughput
- **Network**: Bytes sent/received, packet counters
- **Filesystem**: Usage per mount point, inodes

## Grafana Dashboards

### Zero Inertia Overview Dashboard

Pre-configured dashboard with the following panels:

#### Row 1: Key Performance Indicators
- **Total Users**: Stat panel with current count and sparkline
- **Active Users (7d)**: Weekly active user count
- **Active Users (30d)**: Monthly active user count
- **Disk Usage %**: Gauge with color thresholds (green < 70%, yellow 70-85%, red > 85%)

#### Row 2: API Performance
- **Request Rate**: Line chart showing requests/second by endpoint
- **Request Duration**: Multi-line chart with p50, p95, p99 latencies
- **Error Rate**: 4xx and 5xx error counts over time

#### Row 3: Business Metrics
- **Tasks Overview**: Bar gauge showing active vs completed tasks
- **Projects & Notes**: Combined stat panels
- **Media Tracker**: Count of tracked media items

#### Row 4: Infrastructure
- **CPU Usage**: Time series for each core
- **Memory Usage**: Stacked area chart (used, cached, free)
- **Disk Space**: Bar chart showing used vs free space
- **Network Traffic**: In/out bandwidth over time

## Best Practices

### 1. Disk Usage Monitoring (Critical for 40GB Servers)

With limited disk space, monitor these metrics closely:

- **Critical Threshold**: 85% usage (35GB used) → Take immediate action
- **Warning Threshold**: 70% usage (28GB used) → Plan cleanup
- **Healthy Range**: < 60% usage (< 24GB used)

**Grafana Alert Configuration:**
```yaml
Alert: High Disk Usage
Condition: disk_usage_percent > 70
For: 5 minutes
Severity: Warning

Alert: Critical Disk Usage
Condition: disk_usage_percent > 85
For: 1 minute
Severity: Critical
```

### 2. Data Retention Strategy

Current configuration minimizes disk usage:

| Component | Retention | Disk Usage | Can Reduce To |
|-----------|-----------|------------|---------------|
| Prometheus | 7 days | ~500MB | 3 days (~200MB) |
| Grafana | Unlimited | ~50MB | N/A (minimal) |
| Umami DB | Unlimited | ~100MB | Configure cleanup |
| **Total** | - | **~650MB** | - |

### 3. Alerting Best Practices

Set up alerts for:
- **Disk usage** > 70% (warning), > 85% (critical)
- **High error rate** > 5% of requests
- **Slow requests** > 1 second (p99)
- **User inactivity** (no logins for 7 days)
- **Service downtime** (targets down in Prometheus)

### 4. Security Recommendations

- ✅ Change all default passwords immediately
- ✅ Use strong, randomly generated passwords (`openssl rand -base64 32`)
- ✅ Keep monitoring services behind basic auth
- ✅ Enable HTTPS for all monitoring endpoints
- ✅ Restrict Prometheus/Node Exporter to internal network only
- ✅ Review Grafana user permissions regularly
- ✅ Enable Grafana audit logging in production

### 5. Regular Maintenance

**Weekly:**
- Check disk usage trends in Grafana
- Review error rates and slow endpoints
- Verify all Prometheus targets are healthy

**Monthly:**
- Review and prune old Grafana dashboards
- Clean up Umami analytics (if needed)
- Update monitoring stack images (`docker-compose pull`)

**Quarterly:**
- Backup Grafana dashboards and configuration
- Review alerting rules and thresholds
- Audit monitoring access logs

## Privacy & Compliance

### Umami Analytics (GDPR Compliant)

✅ **Privacy-first design:**
- No cookies used
- No personal data collected
- IP addresses salted and hashed
- Referrer data anonymized
- User agent not stored
- Self-hosted (data stays on your server)

✅ **GDPR Compliance:**
- No consent banner required
- No data sharing with third parties
- Full data ownership
- Easy data export/deletion

### Prometheus Metrics

✅ **No PII collected:**
- Only aggregated counters (total users, tasks, etc.)
- No user-identifiable information
- No personal data in labels
- No request payload logging

### Data Retention Policy

Document your retention policy for compliance:

```
Zero Inertia Monitoring Data Retention Policy

1. Prometheus Metrics: 7 days
   - Automatic deletion after retention period
   - No personal data stored

2. Grafana Dashboards: Indefinite
   - Configuration only, no personal data

3. Umami Analytics: 12 months
   - Anonymous page views only
   - Purged after 1 year
```

## Scaling Considerations

### When Your App Grows

#### Add Database Monitoring

Monitor PostgreSQL performance:

```yaml
postgres-exporter:
  image: prometheuscommunity/postgres-exporter:latest
  environment:
    DATA_SOURCE_NAME: "postgresql://user:pass@postgres:5432/dbname?sslmode=disable"
  networks:
    - app-network
```

**Metrics**: Query performance, connection pool, cache hit ratio, locks

#### Add Redis Monitoring

Track cache performance:

```yaml
redis-exporter:
  image: oliver006/redis_exporter:latest
  environment:
    REDIS_ADDR: redis:6379
    REDIS_PASSWORD: ${REDIS_PASSWORD}
  networks:
    - app-network
```

**Metrics**: Hit rate, evictions, memory usage, key count

#### Increase Retention

Keep more historical data:

```yaml
# Prometheus
command:
  - '--storage.tsdb.retention.time=30d'  # 1 month
  - '--storage.tsdb.retention.size=5GB'  # Size limit
```

#### Advanced Alerting

Set up Alertmanager for sophisticated alert routing:

```yaml
alertmanager:
  image: prom/alertmanager:latest
  volumes:
    - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
  networks:
    - app-network
```

**Integrations**: Email, Slack, PagerDuty, Discord, Microsoft Teams

#### Distributed Tracing

Add OpenTelemetry for request tracing:

```python
# Backend instrumentation
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

FastAPIInstrumentor.instrument_app(app)
```

**Benefits**: Trace requests across services, identify bottlenecks, debug issues

## Resource Requirements

### Minimum (Current Setup)

- **CPU**: 0.5 cores total for monitoring stack
- **RAM**: 512MB total
- **Disk**: 1.5GB (with 7-day retention)
- **Network**: Minimal (scraping only)

### Recommended (Production)

- **CPU**: 1 core total
- **RAM**: 1GB total
- **Disk**: 5GB (for 30-day retention + growth)
- **Network**: < 1 Mbps

### High Traffic (100k+ requests/day)

- **CPU**: 2 cores total
- **RAM**: 2GB total
- **Disk**: 10GB (for extended retention)
- **Network**: < 5 Mbps

## Useful Resources

- **Prometheus Documentation**: https://prometheus.io/docs/
- **Grafana Documentation**: https://grafana.com/docs/
- **Umami Documentation**: https://umami.is/docs
- **PromQL Tutorial**: https://prometheus.io/docs/prometheus/latest/querying/basics/
- **Node Exporter Guide**: https://github.com/prometheus/node_exporter

---

**Next Steps**: See [setup.md](./setup.md) for installation and configuration instructions.
