# Deployment Guide for Futu MCP Server

This guide covers deploying the Futu MCP Server in HTTP mode for use with Antigravity and other remote MCP clients.

## Prerequisites

1. **FutuOpenD** running on your machine (localhost:11111)
2. **Docker** installed (for containerized deployment)
3. **Python 3.12+** (for local deployment)

## Local HTTP Deployment

### 1. Install Dependencies

```bash
cd /path/to/futu-mcp
uv sync
```

### 2. Configure Environment

Create or update your `.env` file:

```bash
# FutuOpenD Connection
FUTU_HOST=127.0.0.1
FUTU_PORT=11111

# Server Configuration
SERVER_MODE=http
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Optional: Trading Password
# FUTU_TRADE_PWD=your_password
```

### 3. Run the Server

```bash
# Option 1: Using command line flag
uv run futu-mcp-server --http

# Option 2: Using environment variable
SERVER_MODE=http uv run futu-mcp-server
```

The server will start on `http://0.0.0.0:8000` with:
- Health check: `http://localhost:8000/health`
- MCP endpoint: `http://localhost:8000/mcp`

## Docker Deployment

### 1. Build the Docker Image

```bash
cd /path/to/futu-mcp
docker build -t futu-mcp:latest .
```

### 2. Run with Docker Compose (Recommended)

```bash
# Start the server
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f futu-mcp

# Stop the server
docker-compose down
```

### 3. Run with Docker CLI

**Option A: Host Networking (Easiest)**

```bash
docker run -d \
  --name futu-mcp-server \
  --network host \
  -e FUTU_HOST=127.0.0.1 \
  -e FUTU_PORT=11111 \
  -e SERVER_MODE=http \
  futu-mcp:latest
```

**Option B: Bridge Networking**

```bash
docker run -d \
  --name futu-mcp-server \
  -p 8000:8000 \
  --add-host host.docker.internal:host-gateway \
  -e FUTU_HOST=host.docker.internal \
  -e FUTU_PORT=11111 \
  -e SERVER_MODE=http \
  futu-mcp:latest
```

### 4. Verify Docker Deployment

```bash
# Check health
curl http://localhost:8000/health

# Check logs
docker logs futu-mcp-server

# Test MCP endpoint
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
```

## Antigravity Integration

### 1. Configure Antigravity

Add the Futu MCP server to your Antigravity `mcp_config.json`:

**For local deployment:**
```json
{
  "mcpServers": {
    "futu": {
      "url": "http://localhost:8000/mcp",
      "transport": "http"
    }
  }
}
```

**For Docker deployment on same machine:**
```json
{
  "mcpServers": {
    "futu": {
      "url": "http://localhost:8000/mcp",
      "transport": "http"
    }
  }
}
```

**For remote deployment:**
```json
{
  "mcpServers": {
    "futu": {
      "url": "https://your-server.com/mcp",
      "transport": "http"
    }
  }
}
```

### 2. Restart Antigravity

After updating the configuration, restart Antigravity to load the new MCP server.

### 3. Verify Integration

In Antigravity, you should see 24 Futu tools available:
- 8 Market Data tools
- 9 Trading tools
- 3 Account Management tools
- 2 Watchlist & Alerts tools
- 2 Market Info tools

## Production Deployment with HTTPS

For production use, it's recommended to run the server behind a reverse proxy with SSL/TLS.

### Nginx Reverse Proxy Example

```nginx
server {
    listen 443 ssl http2;
    server_name your-server.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /mcp {
        proxy_pass http://localhost:8000/mcp;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://localhost:8000/health;
    }
}
```

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `FUTU_HOST` | `127.0.0.1` | FutuOpenD host address |
| `FUTU_PORT` | `11111` | FutuOpenD port number |
| `FUTU_TRADE_PWD` | - | Trading password (required for real trading) |
| `FUTU_CONNECTION_TIMEOUT` | `30` | Connection timeout in seconds |
| `FUTU_REQUEST_TIMEOUT` | `60` | Request timeout in seconds |
| `FUTU_MAX_SUBSCRIPTION_QUOTA` | `500` | Maximum subscription quota |
| `SERVER_MODE` | `stdio` | Server mode: `stdio` or `http` |
| `SERVER_HOST` | `0.0.0.0` | Server bind address |
| `SERVER_PORT` | `8000` | Server port |
| `LOG_LEVEL` | `INFO` | Logging level |

## Troubleshooting

### Server won't start in HTTP mode

**Error**: `ModuleNotFoundError: No module named 'uvicorn'`

**Solution**: Install dependencies
```bash
uv sync
```

### Can't connect to FutuOpenD from Docker

**Error**: Connection refused to FutuOpenD

**Solution**: 
1. Ensure FutuOpenD is running on host
2. Use host networking mode in docker-compose.yml
3. Or use `host.docker.internal` as FUTU_HOST with bridge networking

### Health check fails

**Error**: Health check endpoint returns 404

**Solution**: Ensure server is running in HTTP mode (`--http` flag or `SERVER_MODE=http`)

### Antigravity can't connect

**Error**: Connection timeout or refused

**Solution**:
1. Verify server is running: `curl http://localhost:8000/health`
2. Check firewall settings
3. Ensure correct URL in Antigravity config
4. Check server logs: `docker logs futu-mcp-server`

## Security Considerations

### Authentication

The current implementation does not include authentication. For production:

1. **Add API Key Authentication**: Implement middleware to validate API keys
2. **Use Reverse Proxy**: Let nginx/Apache handle authentication
3. **Network Isolation**: Use VPN or private network

### SSL/TLS

For production deployments:
- Use HTTPS (reverse proxy with SSL/TLS)
- Use valid SSL certificates (Let's Encrypt)
- Disable HTTP access

### Firewall

- Restrict access to port 8000
- Only allow connections from trusted IPs
- Use Docker network isolation

## Monitoring

### Health Checks

```bash
# Simple health check
curl http://localhost:8000/health

# Continuous monitoring
watch -n 5 'curl -s http://localhost:8000/health | jq'
```

### Logs

```bash
# Docker logs
docker logs -f futu-mcp-server

# Local deployment logs
# Logs are output to stdout
```

## Backup and Recovery

### Configuration Backup

```bash
# Backup .env file
cp .env .env.backup

# Backup docker-compose.yml
cp docker-compose.yml docker-compose.yml.backup
```

### Rollback to stdio Mode

If issues occur, you can always rollback to stdio mode:

```bash
# Stop Docker container
docker-compose down

# Run in stdio mode
uv run futu-mcp-server
```

## Performance Tuning

### Uvicorn Workers

For high-traffic deployments, use multiple workers:

```python
# In server.py, modify uvicorn.run():
uvicorn.run(
    create_app(),
    host=config.server_host,
    port=config.server_port,
    workers=4,  # Add multiple workers
    log_level=config.log_level.lower()
)
```

### Docker Resources

Limit Docker container resources:

```yaml
# In docker-compose.yml
services:
  futu-mcp:
    # ... other config ...
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '1'
          memory: 512M
```

## Next Steps

1. Test the deployment with sample queries
2. Monitor performance and logs
3. Set up automated backups
4. Implement authentication for production
5. Configure SSL/TLS with reverse proxy
