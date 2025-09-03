# 🐳 Docker Deployment Guide

## Overview

This guide shows you how to deploy your RAG application using Docker, which provides:
- **Consistent environment** across different machines
- **Easy scaling** and deployment
- **Isolation** from system dependencies
- **Portability** across different platforms

## Prerequisites

1. **Docker installed** on your system
2. **Docker Compose** installed
3. **Git** to clone your repository

## Quick Start

### 1. Clone and Setup

```bash
# Clone your repository
git clone https://github.com/shakthiveluk/rag-app.git
cd rag-app

# Copy environment file
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### 2. Set Environment Variables

Edit `.env` file with your actual values:

```bash
# Required
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Optional (have defaults)
VECTORSTORE=FAISS
EMBEDDINGS=HF
LLM_PROVIDER=OPENAI
OPENAI_MODEL=gpt-4o-mini
```

### 3. Deploy with Script

```bash
# Make script executable
chmod +x deploy-docker.sh

# Run deployment script
./deploy-docker.sh
```

## Manual Deployment

### Option 1: Docker Compose (Recommended)

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Option 2: Docker Direct

```bash
# Build image
docker build -t rag-app .

# Run container
docker run -d \
  --name rag-app \
  -p 8501:8501 \
  --env-file .env \
  rag-app

# View logs
docker logs rag-app

# Stop
docker stop rag-app
```

## Docker Commands Reference

### Building

```bash
# Build image
docker build -t rag-app .

# Build with no cache
docker build --no-cache -t rag-app .

# Build with specific platform
docker build --platform linux/amd64 -t rag-app .
```

### Running

```bash
# Run in foreground
docker run -p 8501:8501 --env-file .env rag-app

# Run in background
docker run -d -p 8501:8501 --env-file .env --name rag-app rag-app

# Run with volume mounts
docker run -d \
  -p 8501:8501 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/uploads:/app/uploads \
  --name rag-app \
  rag-app
```

### Management

```bash
# List containers
docker ps -a

# List images
docker images

# View logs
docker logs rag-app

# Execute commands in container
docker exec -it rag-app bash

# Stop container
docker stop rag-app

# Remove container
docker rm rag-app

# Remove image
docker rmi rag-app
```

## Docker Compose Commands

```bash
# Start services
docker-compose up -d

# Start with rebuild
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Restart services
docker-compose restart
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | `sk-1234567890abcdef...` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VECTORSTORE` | `FAISS` | Vector store type |
| `EMBEDDINGS` | `HF` | Embeddings provider |
| `LLM_PROVIDER` | `OPENAI` | LLM provider |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model |

## Volume Mounts

The Docker setup includes these volume mounts:

- `./data:/app/data` - Persistent data storage
- `./uploads:/app/uploads` - File upload storage

## Health Checks

The Docker container includes health checks:

```bash
# Check container health
docker inspect rag-app | grep Health -A 10

# View health check logs
docker logs rag-app | grep health
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using port 8501
   sudo lsof -i :8501
   
   # Use different port
   docker run -p 8502:8501 --env-file .env rag-app
   ```

2. **Permission denied**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

3. **Build fails**
   ```bash
   # Clean Docker cache
   docker system prune -a
   
   # Rebuild without cache
   docker build --no-cache -t rag-app .
   ```

4. **Container exits immediately**
   ```bash
   # Check logs
   docker logs rag-app
   
   # Run in foreground to see errors
   docker run -p 8501:8501 --env-file .env rag-app
   ```

### Debug Commands

```bash
# Check container status
docker ps -a

# View container details
docker inspect rag-app

# Check resource usage
docker stats rag-app

# View container filesystem
docker exec -it rag-app ls -la
```

## Production Deployment

### 1. Environment Variables

```bash
# Production .env
OPENAI_API_KEY=sk-your-production-key
VECTORSTORE=ATLAS
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/rag_demo
```

### 2. Docker Compose Production

```yaml
version: '3.8'

services:
  rag-app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - VECTORSTORE=ATLAS
      - MONGODB_URI=${MONGODB_URI}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 3. Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Security Considerations

1. **Never commit API keys** to Git
2. **Use environment variables** for sensitive data
3. **Limit container permissions** in production
4. **Regular security updates** for base images
5. **Network isolation** in production

## Performance Optimization

1. **Multi-stage builds** for smaller images
2. **Layer caching** for faster builds
3. **Resource limits** for containers
4. **Health checks** for monitoring
5. **Log rotation** for disk space

## Monitoring

```bash
# Resource usage
docker stats

# Container logs
docker logs -f rag-app

# System resources
docker system df

# Clean up unused resources
docker system prune
```

## Next Steps

After successful Docker deployment:

1. **Test your application** at `http://localhost:8501`
2. **Upload and process documents**
3. **Ask questions** about your documents
4. **Monitor performance** and logs
5. **Scale up** as needed

## Support

If you encounter issues:

1. **Check the logs**: `docker logs rag-app`
2. **Verify environment variables**: `docker exec rag-app env`
3. **Check container health**: `docker inspect rag-app`
4. **Review this guide** for troubleshooting steps

---

**Happy Deploying! 🚀**
