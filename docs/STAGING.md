# Staging Environment

This staging environment mirrors the production setup but runs locally with exposed ports for testing before deployment.

## Architecture

**All services run in Docker containers** (mirrors production architecture):
- **Caddy**: Reverse proxy with automatic routing (same as production)
- **Frontend**: Vue.js production build served by Nginx (inside container)
- **Backend**: FastAPI with metrics enabled
- **PostgreSQL**: Separate staging database
- **Redis**: Separate staging cache
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboard
- **Node Exporter**: System metrics

## Quick Start

### 1. Build and start all services

```bash
docker compose --env-file backend/.env.staging -f docker-compose.staging.yml up -d
```

### 2. Run database migrations

```bash
docker exec zero_inertia_backend_staging alembic upgrade head
```

### 3. Access the services

- **Main App** (via Caddy): http://localhost:8082
- **Grafana** (via Caddy): http://localhost:8082/grafana/ (auto-redirects to /grafana/login)
  - Default credentials: admin / admin (from GRAFANA_ADMIN_PASSWORD in .env.staging)
- **Backend API** (direct): http://localhost:8001/api/v1
- **Frontend** (direct): http://localhost:8080
- **Grafana** (direct): http://localhost:3002
- **Prometheus**: http://localhost:9091
- **PostgreSQL**: `localhost:5433`
- **Redis**: `localhost:6380`

## Port Mapping

All ports are offset to avoid conflicts with development environment:

| Service | Dev Port | Staging Port | Production |
|---------|----------|--------------|------------|
| Backend | 8000 | 8001 | Internal |
| Frontend | 5173 | 8080 | Internal |
| Caddy | - | 8082 | 80/443 |
| PostgreSQL | 5432 | 5433 | Internal |
| Redis | 6379 | 6380 | Internal |
| Prometheus | - | 9091 | Internal |
| Grafana | - | 3002 | Subdomain |
| Node Exporter | - | 9101 | Internal |

## Testing Checklist

Before deploying to production, verify:

- [ ] All containers start successfully
- [ ] Backend health check passes: `curl http://localhost:8001/health`
- [ ] Database migrations apply cleanly
- [ ] Frontend loads and connects to backend
- [ ] OAuth authentication flow works
- [ ] Prometheus scrapes all targets successfully
- [ ] Grafana dashboard displays metrics (no NaN values)
- [ ] System metrics (CPU, RAM, Disk) show in Grafana
- [ ] Application metrics (users, tasks) show in Grafana
- [ ] Caddy routes all requests correctly
- [ ] Grafana accessible via http://localhost:8082/grafana/

## Useful Commands

### View logs for all services
```bash
docker compose --env-file backend/.env.staging -f docker-compose.staging.yml logs -f
```

### View logs for specific service
```bash
docker logs zero_inertia_backend_staging -f
docker logs zero_inertia_caddy_staging -f
docker logs zero_inertia_grafana_staging -f
```

### Restart a service
```bash
docker compose --env-file backend/.env.staging -f docker-compose.staging.yml restart backend
```

### Stop all services
```bash
docker compose --env-file backend/.env.staging -f docker-compose.staging.yml down
```

### Stop and remove volumes (clean slate)
```bash
docker compose --env-file backend/.env.staging -f docker-compose.staging.yml down -v
```

### Rebuild after code changes
```bash
docker compose --env-file backend/.env.staging -f docker-compose.staging.yml up -d --build backend frontend
```

### Check Prometheus targets health
```bash
curl -s http://localhost:9091/api/v1/targets | python3 -c "import sys, json; data=json.load(sys.stdin); print('\n'.join([f\"{t['labels']['job']:20} -> {t['scrapeUrl']:40} [{t['health']}]\" for t in data['data']['activeTargets']]))"
```

### Access backend shell
```bash
docker exec -it zero_inertia_backend_staging sh
```

### Access PostgreSQL
```bash
docker exec -it zero_inertia_db_staging psql -U postgres -d zeroinertia_staging
```

## Environment Variables

Staging uses the same `.env` files as production:
- `backend/.env.staging` - Backend configuration
- `frontend/.env` - Frontend configuration

Make sure these are properly configured before starting staging.

## Troubleshooting

### Backend fails to start
- Check environment variables in `backend/.env.staging`
- Ensure database is healthy: `docker compose --env-file backend/.env.staging -f docker-compose.staging.yml ps postgres`
- View logs: `docker logs zero_inertia_backend_staging`

### Prometheus shows targets as "down"
- Wait 15-30 seconds after startup for first scrape
- Check if services are healthy: `docker compose --env-file backend/.env.staging -f docker-compose.staging.yml ps`
- Verify network connectivity from Prometheus container

### Grafana shows "NaN" in dashboard
- Verify datasource UID matches in `grafana/provisioning/datasources/prometheus.yml`
- Check Prometheus is scraping successfully
- Ensure backend has `ENABLE_METRICS=true` in environment

### Database connection refused
- Ensure PostgreSQL container is healthy
- Check `POSTGRES_HOST=postgres` in backend environment
- Verify network connectivity: `docker exec zero_inertia_backend_staging ping postgres`
