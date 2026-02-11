# 🐳 Docker Setup Guide - Logistics AI Bot

This guide explains how to run the Logistics AI Bot using Docker.

---

## 📋 Prerequisites

1. **Docker Desktop** installed on your system
   - **Mac**: [Download Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
   - **Windows**: [Download Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
   - **Linux**: Install Docker Engine and Docker Compose

2. **Databricks API Token**
   - You need a valid Databricks token to access the Claude 3.7 Sonnet model
   - Get it from your Databricks workspace

---

## 🚀 Quick Start (3 Steps)

### Step 1: Create Environment File

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Databricks token
nano .env  # or use any text editor
```

**Edit `.env` file:**
```bash
DATABRICKS_TOKEN=dapi81b45be7f09611a410fc3e5104a8cadf-3
DATABRICKS_BASE_URL=https://adb-1825279086009288.8.azuredatabricks.net/serving-endpoints
MODEL_ENDPOINT_ID=databricks-claude-3-7-sonnet
```

### Step 2: Build and Run

```bash
# Build and start the container
docker-compose up -d
```

### Step 3: Access the Application

- **Frontend UI**: http://localhost:5002
- **API Server**: http://localhost:5001
- **API Documentation**: http://localhost:5001/docs

---

## 🛠️ Detailed Usage

### Building the Docker Image

```bash
# Build the image
docker-compose build

# Or build manually
docker build -t logistics-ai-bot .
```

### Running the Container

**Option 1: Using Docker Compose (Recommended)**
```bash
# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

**Option 2: Using Docker Run**
```bash
docker run -d \
  --name logistics-ai-bot \
  -p 5001:5001 \
  -p 5002:5002 \
  -e DATABRICKS_TOKEN=your_token_here \
  -e DATABRICKS_BASE_URL=https://adb-1825279086009288.8.azuredatabricks.net/serving-endpoints \
  -e MODEL_ENDPOINT_ID=databricks-claude-3-7-sonnet \
  -v $(pwd)/data/threads:/app/data/threads \
  -v $(pwd)/logs:/app/logs \
  logistics-ai-bot
```

### Viewing Logs

```bash
# All logs
docker-compose logs -f

# API server logs only
docker-compose logs -f logistics-ai-bot | grep "api_server"

# Inside container
docker exec -it logistics-ai-bot tail -f /app/logs/api_server.log
```

### Stopping the Container

```bash
# Stop and remove
docker-compose down

# Stop without removing
docker-compose stop

# Restart
docker-compose restart
```

---

## 📦 What's Included in the Image

The Docker image contains:
- ✅ Python 3.12 runtime
- ✅ All required dependencies (LangGraph, LangChain, FastAPI, etc.)
- ✅ 20+ specialized AI agents
- ✅ API server (FastAPI)
- ✅ Frontend web interface
- ✅ Configuration files
- ✅ Data processing utilities

**Image Size**: ~800MB (optimized with multi-stage build)

---

## 🔧 Configuration Options

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABRICKS_TOKEN` | ✅ Yes | - | Your Databricks API token |
| `DATABRICKS_BASE_URL` | No | (preset) | Databricks endpoint URL |
| `MODEL_ENDPOINT_ID` | No | `databricks-claude-3-7-sonnet` | Model endpoint name |
| `API_PORT` | No | `5001` | API server port |
| `FRONTEND_PORT` | No | `5002` | Frontend server port |

### Volume Mounts

The Docker setup mounts two directories:

1. **Thread Data**: `./data/threads` → `/app/data/threads`
   - Persists conversation threads
   - Survives container restarts

2. **Logs**: `./logs` → `/app/logs`
   - API and frontend logs
   - Useful for debugging

---

## 🐛 Troubleshooting

### Container Won't Start

**Check if token is set:**
```bash
docker-compose logs logistics-ai-bot | grep "DATABRICKS_TOKEN"
```

**If you see "DATABRICKS_TOKEN environment variable is not set":**
- Make sure `.env` file exists
- Verify token is set in `.env`
- Try: `docker-compose down && docker-compose up -d`

### API Server Not Responding

**Check health:**
```bash
curl http://localhost:5001/health
```

**Check logs:**
```bash
docker-compose logs -f logistics-ai-bot
```

**Common issues:**
- Token is invalid or expired
- Network connectivity to Databricks endpoint
- Port 5001 is already in use

### Frontend Not Loading

**Check if frontend is running:**
```bash
curl http://localhost:5002
```

**Check logs:**
```bash
docker exec -it logistics-ai-bot tail -f /app/logs/frontend_server.log
```

### Reset Everything

```bash
# Stop and remove containers, volumes
docker-compose down -v

# Remove image
docker rmi logistics-ai-bot

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

---

## 🌐 Publishing to Docker Hub (Optional)

If you want to share the image with others:

### 1. Build and Tag
```bash
docker build -t your-dockerhub-username/logistics-ai-bot:latest .
docker tag your-dockerhub-username/logistics-ai-bot:latest your-dockerhub-username/logistics-ai-bot:v1.0.0
```

### 2. Push to Docker Hub
```bash
docker login
docker push your-dockerhub-username/logistics-ai-bot:latest
docker push your-dockerhub-username/logistics-ai-bot:v1.0.0
```

### 3. Others Can Pull and Run
```bash
docker pull your-dockerhub-username/logistics-ai-bot:latest
docker run -d \
  -p 5001:5001 -p 5002:5002 \
  -e DATABRICKS_TOKEN=their_token \
  your-dockerhub-username/logistics-ai-bot:latest
```

---

## 🔒 Security Notes

### ⚠️ Important Security Considerations

1. **Never commit `.env` file to Git**
   - Already in `.gitignore`
   - Contains sensitive API tokens

2. **Never publish Docker images with embedded tokens**
   - Always pass tokens via environment variables
   - Never hardcode in Dockerfile or config files

3. **Rotate tokens regularly**
   - Update `.env` file
   - Restart container: `docker-compose restart`

4. **Use secrets management in production**
   - Docker Secrets
   - Kubernetes Secrets
   - AWS Secrets Manager / Azure Key Vault

---

## 📊 Resource Usage

**Typical resource consumption:**
- **CPU**: 0.5-2 cores (during LLM calls)
- **Memory**: 500MB-1GB
- **Disk**: ~1GB (image + data)

**Recommended Docker Desktop settings:**
- Memory: 4GB minimum
- CPUs: 2 minimum
- Disk: 10GB minimum

---

## 🎯 Production Deployment

For production use, consider:

1. **Use Docker Secrets** instead of environment variables
2. **Enable HTTPS** with reverse proxy (nginx/traefik)
3. **Set up monitoring** (Prometheus + Grafana)
4. **Configure log rotation**
5. **Use orchestration** (Kubernetes, Docker Swarm)
6. **Set resource limits** in docker-compose.yml:

```yaml
services:
  logistics-ai-bot:
    # ... other config ...
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

---

## 📞 Support

If you encounter issues:

1. Check logs: `docker-compose logs -f`
2. Verify health: `curl http://localhost:5001/health`
3. Check Docker Desktop is running
4. Ensure ports 5001 and 5002 are not in use
5. Verify your Databricks token is valid

---

## ✅ Quick Reference

```bash
# Build
docker-compose build

# Start
docker-compose up -d

# Logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart

# Shell access
docker exec -it logistics-ai-bot bash

# Health check
curl http://localhost:5001/health

# Access UI
open http://localhost:5002
```

---

**That's it! Your Logistics AI Bot is now containerized and ready to run anywhere Docker is available.** 🎉
