# NMS AI Monitoring

AI-powered network monitoring platform (SME/MSP focused).

## What's running right now
- **Prometheus** → collects metrics
- **Grafana** → shows dashboards
- **Alertmanager** → sends alerts

## How to run it
1. Install Docker Desktop: https://www.docker.com/products/docker-desktop/
2. Open a terminal in this folder
3. Run:
   ```
   docker compose up -d
   ```
4. Open Grafana: http://localhost:3000 (login: admin / admin)
5. Open Prometheus: http://localhost:9090

## Roadmap
- [x] Central server (Prometheus + Grafana + Alertmanager)
- [x] Agent (reports metrics from endpoints)
- [x] AI prediction engine
- [x] Self-healing automation
- [ ] Windows installer