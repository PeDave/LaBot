# Ubuntu 24.04 Deployment Runbook

This guide covers deploying LaBot on Ubuntu 24.04 Server with the domain `labotkripto.com`.

## Prerequisites
- Ubuntu 24.04 Server
- Domain: labotkripto.com (DNS configured to point to server IP)
- Root or sudo access

## 1. Install .NET 8 Runtime

```bash
# Add Microsoft package repository
wget https://packages.microsoft.com/config/ubuntu/24.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
rm packages-microsoft-prod.deb

# Install .NET 8 Runtime
sudo apt-get update
sudo apt-get install -y aspnetcore-runtime-8.0

# Verify installation
dotnet --version
```

## 2. Install PostgreSQL

```bash
# Install PostgreSQL 16
sudo apt-get install -y postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql <<EOF
CREATE DATABASE labot;
CREATE USER labot WITH ENCRYPTED PASSWORD 'CHANGE_ME_IN_PRODUCTION';
GRANT ALL PRIVILEGES ON DATABASE labot TO labot;
ALTER DATABASE labot OWNER TO labot;
\q
EOF
```

## 3. Setup Application User

```bash
# Create application user
sudo useradd -r -m -s /bin/bash labot
sudo mkdir -p /opt/labot
sudo chown labot:labot /opt/labot
```

## 4. Deploy Application

```bash
# Clone repository (or copy built artifacts)
cd /opt/labot
sudo -u labot git clone https://github.com/PeDave/LaBot.git .

# Build application
sudo -u labot dotnet restore
sudo -u labot dotnet build -c Release
sudo -u labot dotnet publish src/LaBot.Web/LaBot.Web.csproj -c Release -o /opt/labot/web
sudo -u labot dotnet publish src/LaBot.Api/LaBot.Api.csproj -c Release -o /opt/labot/api
sudo -u labot dotnet publish src/LaBot.Worker/LaBot.Worker.csproj -c Release -o /opt/labot/worker

# Set up configuration
sudo -u labot cp /opt/labot/ops/config/appsettings.Production.json /opt/labot/web/appsettings.Production.json
```

## 5. Configure Environment Variables

```bash
# Create environment file for secrets
sudo mkdir -p /etc/labot
sudo cat > /etc/labot/web.env <<EOF
ASPNETCORE_ENVIRONMENT=Production
ConnectionStrings__DefaultConnection="Host=localhost;Database=labot;Username=labot;Password=CHANGE_ME"
Stripe__SecretKey="sk_live_YOUR_SECRET_KEY"
Stripe__PublishableKey="pk_live_YOUR_PUBLISHABLE_KEY"
Stripe__WebhookSecret="whsec_YOUR_WEBHOOK_SECRET"
EOF

sudo chmod 600 /etc/labot/web.env
sudo chown labot:labot /etc/labot/web.env
```

## 6. Run Database Migrations

```bash
# Run migrations
cd /opt/labot
sudo -u labot dotnet ef database update --project src/LaBot.Infrastructure/LaBot.Infrastructure.csproj --startup-project src/LaBot.Web/LaBot.Web.csproj --connection "Host=localhost;Database=labot;Username=labot;Password=CHANGE_ME"
```

## 7. Setup systemd Services

Copy service files from `ops/systemd/` directory:

```bash
# Web service
sudo cp /opt/labot/ops/systemd/labot-web.service /etc/systemd/system/
sudo cp /opt/labot/ops/systemd/labot-api.service /etc/systemd/system/
sudo cp /opt/labot/ops/systemd/labot-worker.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start services
sudo systemctl enable labot-web labot-api labot-worker
sudo systemctl start labot-web labot-api labot-worker

# Check status
sudo systemctl status labot-web
sudo systemctl status labot-api
sudo systemctl status labot-worker
```

## 8. Install Nginx

```bash
# Install Nginx
sudo apt-get install -y nginx

# Copy Nginx configuration
sudo cp /opt/labot/ops/nginx/labotkripto.com.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/labotkripto.com.conf /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## 9. Setup SSL with Certbot

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d labotkripto.com -d www.labotkripto.com

# Test auto-renewal
sudo certbot renew --dry-run
```

## 10. Setup Firewall

```bash
# Install ufw if not installed
sudo apt-get install -y ufw

# Allow SSH, HTTP, HTTPS
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'

# Enable firewall
sudo ufw --force enable

# Check status
sudo ufw status
```

## Monitoring and Logs

```bash
# View Web logs
sudo journalctl -u labot-web -f

# View API logs
sudo journalctl -u labot-api -f

# View Worker logs
sudo journalctl -u labot-worker -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Updates

To update the application:

```bash
# Stop services
sudo systemctl stop labot-web labot-api labot-worker

# Pull latest code
cd /opt/labot
sudo -u labot git pull

# Build and publish
sudo -u labot dotnet publish src/LaBot.Web/LaBot.Web.csproj -c Release -o /opt/labot/web
sudo -u labot dotnet publish src/LaBot.Api/LaBot.Api.csproj -c Release -o /opt/labot/api
sudo -u labot dotnet publish src/LaBot.Worker/LaBot.Worker.csproj -c Release -o /opt/labot/worker

# Run migrations
sudo -u labot dotnet ef database update --project src/LaBot.Infrastructure/LaBot.Infrastructure.csproj --startup-project src/LaBot.Web/LaBot.Web.csproj

# Start services
sudo systemctl start labot-web labot-api labot-worker
```

## Backup

```bash
# Backup database
sudo -u postgres pg_dump labot > /backup/labot_$(date +%Y%m%d).sql

# Backup configuration
sudo tar -czf /backup/labot_config_$(date +%Y%m%d).tar.gz /etc/labot/
```

## Troubleshooting

### Service won't start
```bash
# Check service logs
sudo journalctl -u labot-web -n 50
```

### Database connection issues
```bash
# Test connection
psql -h localhost -U labot -d labot
```

### Nginx issues
```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log
```
