# LaBot

[![CI](https://github.com/PeDave/LaBot/actions/workflows/ci.yml/badge.svg)](https://github.com/PeDave/LaBot/actions/workflows/ci.yml)

A multi-tenant cryptocurrency trading bot platform built with .NET 8, Blazor Server, and PostgreSQL.

## 📖 Documentation

**Start here for comprehensive guidance:**
- 📍 **[docs/PROJECT_INDEX.md](docs/PROJECT_INDEX.md)** - Complete project map, architecture guide, and local development quickstart
- ✅ **[docs/CHECKLIST.md](docs/CHECKLIST.md)** - Master development checklist to keep you on track

**Additional resources:**
- [docs/README.md](docs/README.md) - Full documentation index

## Features

- **Multi-tenant Architecture**: Each user gets their own tenant
- **ASP.NET Core Identity**: Cookie-based authentication
- **Role-based Access**: Admin/Pro/Basic/Free tiers
- **Stripe Integration**: Subscription management (Basic/Pro plans)
- **Exchange Support**: Bitget and BingX via adapter pattern
- **Trading Strategies**: Martingale strategy v1 (more to come)
- **Market Data**: OHLCV candles (15m, 30m, 1h, 4h, 1d)
- **Bot Engine**: Background worker service for automated trading
- **n8n Integration**: Webhook support for workflow automation

## Tech Stack

- .NET 8
- Blazor Server
- PostgreSQL with Entity Framework Core 8
- ASP.NET Core Identity
- Stripe.net
- Nginx reverse proxy
- systemd services

## Project Structure

```
LaBot/
├── src/
│   ├── LaBot.Domain/              # Core entities, value objects, enums
│   ├── LaBot.Application/         # Business logic interfaces
│   ├── LaBot.Infrastructure/      # EF Core, data access, external services
│   ├── LaBot.Exchanges.Core/      # Exchange adapter interfaces
│   ├── LaBot.Exchanges.Bitget/    # Bitget exchange adapter
│   ├── LaBot.Exchanges.BingX/     # BingX exchange adapter
│   ├── LaBot.Web/                 # Blazor Server dashboard
│   ├── LaBot.Api/                 # REST API (webhooks, n8n)
│   └── LaBot.Worker/              # Background bot engine
├── tests/                          # Unit and integration tests
├── ops/                           # Deployment files
│   ├── systemd/                   # systemd service files
│   ├── nginx/                     # Nginx configuration
│   └── config/                    # Example configurations
└── docs/                          # Documentation
```

## Quick Start

### Prerequisites

- .NET 8 SDK
- PostgreSQL 14+
- Node.js 18+ (for n8n, optional)

### Database Setup

```bash
# Create database
sudo -u postgres psql
CREATE DATABASE labot;
CREATE USER labot WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE labot TO labot;
\q
```

### Build and Run

```bash
# Clone repository
git clone https://github.com/PeDave/LaBot.git
cd LaBot

# Restore packages
dotnet restore

# Build
dotnet build

# Run migrations
cd src/LaBot.Infrastructure
dotnet ef database update --startup-project ../LaBot.Web/LaBot.Web.csproj

# Run Web application
cd ../LaBot.Web
dotnet run

# Run API (in another terminal)
cd src/LaBot.Api
dotnet run

# Run Worker (in another terminal)
cd src/LaBot.Worker
dotnet run
```

The web application will be available at `https://localhost:5000`

### Configuration

Update `appsettings.json` in each project:

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Database=labot;Username=labot;Password=your_password"
  },
  "Stripe": {
    "SecretKey": "sk_test_...",
    "PublishableKey": "pk_test_...",
    "WebhookSecret": "whsec_..."
  }
}
```

## Documentation

- [Project Index](docs/PROJECT_INDEX.md) - Architecture, navigation, and development guide
- [Development Checklist](docs/CHECKLIST.md) - Systematic development workflow
- [Deployment Guide](docs/DEPLOYMENT.md) - Ubuntu 24.04 deployment instructions
- [Vendor Setup](docs/VENDOR_SETUP.md) - How to vendor JKorf exchange SDKs
- [n8n Setup](docs/N8N_SETUP.md) - n8n installation without Docker
- [Implementation Summary](docs/IMPLEMENTATION_SUMMARY.md) - Technical overview

## Subscription Tiers

- **Free**: 24h delayed data, basic features
- **Basic**: 1-2 symbols, real-time data, manual trading
- **Pro**: Admin-approved symbols, automated trading, all strategies
- **Admin**: Full access to all features and configuration

## Exchange Integration

The platform uses an adapter pattern for exchange integration. Currently supported:

- **Bitget**: Spot and futures trading
- **BingX**: Spot and futures trading

Symbol format: `BTC/USDT`, `ETH/USDT` (adapters convert to exchange-specific formats)

## Development

### Local Development Commands

```bash
# Restore dependencies
dotnet restore LaBot.slnx

# Build in Release mode (same as CI)
dotnet build LaBot.slnx --configuration Release --no-restore /p:TreatWarningsAsErrors=true

# Run all tests (same as CI)
dotnet test LaBot.slnx --configuration Release --no-build --verbosity normal

# Verify code formatting (same as CI)
dotnet format LaBot.slnx --verify-no-changes

# Auto-fix code formatting
dotnet format LaBot.slnx

# Create migration
cd src/LaBot.Infrastructure
dotnet ef migrations add MigrationName --startup-project ../LaBot.Web/LaBot.Web.csproj
```

### Continuous Integration

The repository uses GitHub Actions for CI/CD. The workflow runs on every pull request and push to main:

- ✅ **Build**: Compiles all projects in Release mode with warnings as errors
- ✅ **Test**: Runs all unit and integration tests
- ℹ️ **Format Check**: Reports formatting inconsistencies but does not fail the build

**Note**: The format check is non-blocking to prevent CI failures from minor whitespace/import issues. Developers are encouraged to run `dotnet format LaBot.sln` locally before committing to maintain code consistency.

To ensure your changes pass CI before pushing, run the build and test commands above locally.

## Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for complete Ubuntu 24.04 deployment instructions including:

- PostgreSQL setup
- systemd services
- Nginx reverse proxy
- SSL with Certbot
- Firewall configuration

## Security

- Secrets loaded from environment variables (not in appsettings.json)
- Per-tenant exchange API keys encrypted in database
- HTTPS enforced in production
- Role-based authorization throughout the application
- Stripe webhook signature verification

## Contributing

This is a private project. Please contact the maintainer for contribution guidelines.

## License

Proprietary - All rights reserved.
