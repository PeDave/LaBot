# n8n Installation Without Docker

This guide covers installing n8n on Ubuntu 24.04 without Docker, using Node.js and systemd.

## Prerequisites
- Ubuntu 24.04 Server
- Node.js 18 or higher
- npm or pnpm

## 1. Install Node.js

```bash
# Install Node.js 20 LTS
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

## 2. Install n8n Globally

```bash
# Install n8n globally
sudo npm install -g n8n

# Verify installation
n8n --version
```

## 3. Create n8n User

```bash
# Create dedicated user for n8n
sudo useradd -r -m -s /bin/bash n8n
sudo mkdir -p /home/n8n/.n8n
sudo chown -R n8n:n8n /home/n8n
```

## 4. Configure n8n

```bash
# Create configuration file
sudo mkdir -p /etc/n8n
sudo cat > /etc/n8n/config <<EOF
# n8n Configuration
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=CHANGE_ME_IN_PRODUCTION
N8N_HOST=localhost
N8N_PORT=5678
N8N_PROTOCOL=http
N8N_EDITOR_BASE_URL=http://localhost:5678
WEBHOOK_URL=https://labotkripto.com/n8n-webhooks
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=localhost
DB_POSTGRESDB_PORT=5432
DB_POSTGRESDB_DATABASE=n8n
DB_POSTGRESDB_USER=n8n
DB_POSTGRESDB_PASSWORD=CHANGE_ME
EXECUTIONS_DATA_SAVE_ON_SUCCESS=all
EXECUTIONS_DATA_SAVE_ON_ERROR=all
N8N_LOG_LEVEL=info
EOF

sudo chmod 600 /etc/n8n/config
sudo chown n8n:n8n /etc/n8n/config
```

## 5. Setup PostgreSQL for n8n

```bash
# Create n8n database
sudo -u postgres psql <<EOF
CREATE DATABASE n8n;
CREATE USER n8n WITH ENCRYPTED PASSWORD 'CHANGE_ME_IN_PRODUCTION';
GRANT ALL PRIVILEGES ON DATABASE n8n TO n8n;
ALTER DATABASE n8n OWNER TO n8n;
\q
EOF
```

## 6. Create systemd Service

Create `/etc/systemd/system/n8n.service`:

```ini
[Unit]
Description=n8n - Workflow Automation Tool
After=network.target postgresql.service

[Service]
Type=simple
User=n8n
EnvironmentFile=/etc/n8n/config
WorkingDirectory=/home/n8n
ExecStart=/usr/bin/n8n start
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Apply the service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable and start n8n
sudo systemctl enable n8n
sudo systemctl start n8n

# Check status
sudo systemctl status n8n
```

## 7. Configure Nginx Reverse Proxy

Add to your Nginx configuration (`/etc/nginx/sites-available/labotkripto.com.conf`):

```nginx
# n8n webhook endpoint
location /n8n-webhooks/ {
    proxy_pass http://localhost:5678/webhook/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# n8n editor (if exposing publicly - use with caution)
location /n8n/ {
    proxy_pass http://localhost:5678/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
    
    # Optional: Restrict access
    allow 192.168.1.0/24;  # Your office IP
    deny all;
}
```

Reload Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 8. Accessing n8n

- **Editor**: http://localhost:5678 (or via Nginx reverse proxy)
- **Webhooks**: https://labotkripto.com/n8n-webhooks/

## LaBot Integration

### From LaBot to n8n

LaBot can trigger n8n workflows via webhooks:

```bash
# Example: Trigger n8n workflow when bot generates signal
curl -X POST https://labotkripto.com/n8n-webhooks/your-webhook-id \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC/USDT",
    "action": "buy",
    "price": 45000,
    "quantity": 0.001
  }'
```

### From n8n to LaBot

n8n can send signals back to LaBot via the API:

```bash
# Example n8n HTTP Request node
POST https://labotkripto.com/api/N8nWebhook/signal
Content-Type: application/json

{
  "signalId": "signal-123",
  "symbol": "BTC/USDT",
  "action": "buy",
  "price": 45000,
  "quantity": 0.001
}
```

### From LaBot Export to n8n

n8n can pull data from LaBot:

```bash
# Example: Get wallet snapshots
GET https://labotkripto.com/api/N8nWebhook/export?tenantId=xxx&dataType=wallet
```

## Example n8n Workflows

### 1. Alert on Large Price Movement

```
Webhook Trigger (LaBot price updates)
  → Filter (price change > 5%)
    → Send Email/Telegram
```

### 2. Auto-rebalance Portfolio

```
Schedule (daily at 9am)
  → HTTP Request (get LaBot wallet)
    → Function (calculate rebalance)
      → HTTP Request (send signal to LaBot)
```

### 3. Multi-exchange Arbitrage

```
Webhook (LaBot price updates - Exchange A)
  → HTTP Request (get price from Exchange B)
    → Function (calculate spread)
      → If spread > threshold
        → HTTP Request (send signals to LaBot)
```

## Monitoring

```bash
# View n8n logs
sudo journalctl -u n8n -f

# Check n8n status
sudo systemctl status n8n

# Restart n8n
sudo systemctl restart n8n
```

## Updates

```bash
# Update n8n to latest version
sudo npm update -g n8n

# Restart service
sudo systemctl restart n8n
```

## Backup

```bash
# Backup n8n database
sudo -u postgres pg_dump n8n > /backup/n8n_$(date +%Y%m%d).sql

# Backup n8n workflows (stored in DB, but also export manually)
# Go to n8n editor → Settings → Export workflows
```

## Security Considerations

1. **Use Basic Auth**: Always enable N8N_BASIC_AUTH_ACTIVE
2. **Restrict Access**: Use Nginx IP restrictions for editor access
3. **HTTPS Only**: Always use HTTPS for webhooks
4. **Webhook Security**: Use unique, long webhook IDs
5. **API Keys**: If integrating with external services, store credentials securely

## Troubleshooting

### n8n won't start

```bash
# Check logs
sudo journalctl -u n8n -n 50

# Check permissions
sudo chown -R n8n:n8n /home/n8n
```

### Database connection issues

```bash
# Test PostgreSQL connection
psql -h localhost -U n8n -d n8n
```

### Webhook not working

```bash
# Check Nginx configuration
sudo nginx -t

# Check n8n logs
sudo journalctl -u n8n -f
```
