# LaBot Project Index

> **Single source of truth** for navigating the LaBot cryptocurrency trading bot platform.

## What is LaBot?

LaBot is a **multi-tenant cryptocurrency trading bot platform** built with .NET 8, Blazor Server, and PostgreSQL. It provides automated trading capabilities across multiple exchanges (Bitget, BingX) with subscription-based access tiers, real-time market data, and workflow automation via n8n integration.

**Core Value Proposition:**
- Multi-user platform where each user starts with their own tenant
- Role-based access control (Admin/Pro/Basic/Free)
- Exchange-agnostic architecture via adapter pattern
- Background worker for automated trading strategies
- Subscription management via Stripe

---

## Architecture at a Glance

LaBot follows **Clean Architecture** principles with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                   Presentation Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  LaBot.Web   │  │  LaBot.Api   │  │ LaBot.Worker │  │
│  │ (Blazor UI)  │  │ (REST API)   │  │ (Bot Engine) │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Application Layer                      │
│              ┌──────────────────────┐                    │
│              │ LaBot.Application    │                    │
│              │ (Business Logic)     │                    │
│              └──────────────────────┘                    │
└─────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Domain Layer                          │
│              ┌──────────────────────┐                    │
│              │   LaBot.Domain       │                    │
│              │ (Entities, Enums)    │                    │
│              └──────────────────────┘                    │
└─────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│                 Infrastructure Layer                     │
│  ┌──────────────────────┐  ┌───────────────────────┐   │
│  │ LaBot.Infrastructure │  │ Exchange Adapters     │   │
│  │ (EF Core, Data)      │  │ ┌─────────────────┐   │   │
│  └──────────────────────┘  │ │ Exchanges.Core  │   │   │
│                             │ │ Exchanges.Bitget│   │   │
│                             │ │ Exchanges.BingX │   │   │
│                             │ └─────────────────┘   │   │
│                             └───────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Project Responsibilities

| Project | Purpose | Key Components |
|---------|---------|----------------|
| **LaBot.Web** | Blazor Server dashboard | Login, Registration, Dashboard, Account Management |
| **LaBot.Api** | REST API endpoints | n8n webhooks, Stripe webhooks, External integrations |
| **LaBot.Worker** | Background bot engine | Trading strategies, Market data polling, Order execution |
| **LaBot.Application** | Business logic interfaces | Service contracts, DTOs, Application logic |
| **LaBot.Domain** | Core business entities | Entities, Value Objects, Enums, Domain logic |
| **LaBot.Infrastructure** | Data & external services | EF Core DbContext, Repositories, External service clients |
| **LaBot.Exchanges.Core** | Exchange abstractions | IExchangeAdapter, IExchangeWebSocketClient interfaces |
| **LaBot.Exchanges.Bitget** | Bitget integration | Bitget-specific adapter implementation |
| **LaBot.Exchanges.BingX** | BingX integration | BingX-specific adapter implementation |

---

## Where to Find What

### 🔐 Authentication & Authorization
- **Identity Setup**: `src/LaBot.Web/Program.cs` - ASP.NET Core Identity configuration
- **Login/Register Pages**: `src/LaBot.Web/Components/Account/` - Login.razor, Register.razor, Logout.razor
- **User Entity**: `src/LaBot.Domain/Entities/User.cs`
- **Roles**: Admin, Pro, Basic, Free (configured in Identity)
- **Authorization**: Cookie-based authentication

### 🏢 Tenancy
- **Tenant Entity**: `src/LaBot.Domain/Entities/Tenant.cs`
- **Tenant Context**: `src/LaBot.Infrastructure/Data/ApplicationDbContext.cs`
- **Current Implementation**: Shared PostgreSQL database + TenantId column
- **Isolation Strategy**: Row-level filtering via TenantId (tenant = user initially)
- **Future Plan**: Multiple users per tenant (organization-level tenancy)

### 💳 Stripe Integration
- **Webhook Controller**: `src/LaBot.Api/Controllers/StripeWebhookController.cs`
- **Subscription Plans**: Basic, Pro (Free is internal-only)
- **Events Handled**: checkout.session.completed, customer.subscription.*
- **Configuration**: Stripe keys in environment variables (see Configuration section)

### 📊 Exchange Integrations
- **Adapter Interfaces**: `src/LaBot.Exchanges.Core/Abstractions/IExchangeAdapter.cs`
- **Bitget Adapter**: `src/LaBot.Exchanges.Bitget/BitgetAdapter.cs`
- **BingX Adapter**: `src/LaBot.Exchanges.BingX/BingXAdapter.cs`
- **Symbol Format**: Internal format is `BTC/USDT` (adapters convert to exchange-specific)
- **SDK Vendoring**: See [VENDOR_SETUP.md](VENDOR_SETUP.md)

### 📈 Market Data
- **Candle Entity**: `src/LaBot.Domain/Entities/Candle.cs`
- **Supported Timeframes**: 15m, 30m, 1h, 4h, 1d
- **Storage**: PostgreSQL via EF Core
- **Data Source**: Exchange REST APIs or WebSocket feeds

### 🤖 Worker & Trading Strategies
- **Worker Service**: `src/LaBot.Worker/Program.cs` - Background service host
- **Strategy Interface**: `src/LaBot.Application/` - Strategy contracts
- **Martingale Strategy**: Implemented in Worker project
- **Bot State**: `src/LaBot.Domain/Entities/BotState.cs`
- **Signals**: `src/LaBot.Domain/Entities/Signal.cs`

### 💾 Persistence & Entity Framework
- **DbContext**: `src/LaBot.Infrastructure/Data/ApplicationDbContext.cs`
- **Migrations**: `src/LaBot.Infrastructure/Migrations/`
- **Initial Migration**: `20260206121508_InitialCreate`
- **Running Migrations**: See Local Development section below

---

## Local Development Quickstart

### Prerequisites
- .NET 8 SDK ([download](https://dotnet.microsoft.com/download/dotnet/8.0))
- PostgreSQL 14+ (local or Docker)
- Node.js 18+ (optional, for n8n)

### 1. Clone and Restore
```bash
git clone https://github.com/PeDave/LaBot.git
cd LaBot

# Restore NuGet packages
dotnet restore

# Build solution
dotnet build
```

### 2. Database Setup
```bash
# Create PostgreSQL database
sudo -u postgres psql
CREATE DATABASE labot;
CREATE USER labot WITH ENCRYPTED PASSWORD 'dev_password';
GRANT ALL PRIVILEGES ON DATABASE labot TO labot;
\q

# Run EF Core migrations
cd src/LaBot.Infrastructure
dotnet ef database update --startup-project ../LaBot.Web/LaBot.Web.csproj
```

### 3. Configuration
Update `appsettings.Development.json` in each project (Web, Api, Worker) or use environment variables:

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Database=labot;Username=labot;Password=dev_password"
  },
  "Stripe": {
    "SecretKey": "sk_test_...",
    "PublishableKey": "pk_test_...",
    "WebhookSecret": "whsec_..."
  }
}
```

### 4. Run Projects
Open three terminal windows:

**Terminal 1 - Web Application:**
```bash
cd src/LaBot.Web
dotnet run
# Access at: https://localhost:5000
```

**Terminal 2 - API:**
```bash
cd src/LaBot.Api
dotnet run
# Access at: https://localhost:5001
```

**Terminal 3 - Worker:**
```bash
cd src/LaBot.Worker
dotnet run
# Check logs for bot activity
```

### 5. Run Tests
```bash
# Run all tests
dotnet test

# Run specific test project
dotnet test tests/LaBot.Domain.Tests/
```

### 6. Create New Migration
```bash
cd src/LaBot.Infrastructure
dotnet ef migrations add YourMigrationName --startup-project ../LaBot.Web/LaBot.Web.csproj
dotnet ef database update --startup-project ../LaBot.Web/LaBot.Web.csproj
```

---

## Primary URLs & Endpoints

### LaBot.Web (Port 5000)
- **Homepage**: `https://localhost:5000/`
- **Login**: `https://localhost:5000/Account/Login`
- **Register**: `https://localhost:5000/Account/Register`
- **Logout**: `https://localhost:5000/Account/Logout`
- **Dashboard**: `https://localhost:5000/` (requires authentication)

### LaBot.Api (Port 5001)
- **Health Check**: `https://localhost:5001/health` (if implemented)
- **Stripe Webhook**: `https://localhost:5001/api/StripeWebhook`
- **n8n Signal Webhook**: `https://localhost:5001/api/N8nWebhook/signal`
- **n8n Export Endpoint**: `https://localhost:5001/api/N8nWebhook/export?tenantId=xxx&dataType=wallet`

### LaBot.Worker
- Background service (no HTTP endpoints)
- Monitor via application logs

### Production URLs (labotkripto.com)
- **Web**: `https://labotkripto.com/`
- **API**: `https://labotkripto.com/api/`
- **n8n Webhooks**: `https://labotkripto.com/n8n-webhooks/`

---

## Configuration & Secrets

### Configuration Hierarchy
1. **appsettings.json** - Default configuration (committed to repo)
2. **appsettings.Development.json** - Development overrides (committed to repo)
3. **appsettings.Production.json** - Production overrides (NOT committed)
4. **Environment Variables** - Runtime overrides (highest priority)

### Secrets Management

**✅ DO:** Store secrets in environment variables
```bash
export ConnectionStrings__DefaultConnection="Host=..."
export Stripe__SecretKey="sk_live_..."
export Stripe__WebhookSecret="whsec_..."
```

**❌ DON'T:** Store secrets in appsettings.json files committed to the repository

### Key Configuration Items
- `ConnectionStrings:DefaultConnection` - PostgreSQL connection string
- `Stripe:SecretKey` - Stripe API secret key
- `Stripe:PublishableKey` - Stripe publishable key (safe to expose to client)
- `Stripe:WebhookSecret` - Stripe webhook signature verification secret
- Exchange API keys are stored **encrypted per-tenant in database** (not in config files)

### Related Documentation
- **Production Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md) - Complete Ubuntu 24.04 deployment guide
- **Exchange SDK Setup**: [VENDOR_SETUP.md](VENDOR_SETUP.md) - How to vendor JKorf SDKs
- **n8n Integration**: [N8N_SETUP.md](N8N_SETUP.md) - n8n installation without Docker
- **Implementation Summary**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Technical overview

---

## Tenancy Architecture

### Current Implementation: Shared Database + TenantId

LaBot uses a **shared database with tenant isolation via TenantId column**:

- **Database**: Single PostgreSQL database (`labot`)
- **Tenant Identification**: `TenantId` column on all tenant-specific tables
- **Initial Model**: `tenant = user` (each registered user gets their own tenant)
- **Isolation**: Row-level filtering via EF Core query filters

**Tenant-specific entities:**
- User (belongs to Tenant)
- ExchangeApiKey (tenant-specific exchange credentials)
- BotState (tenant's bot configuration)
- Signal (tenant's trading signals)
- WalletSnapshot (tenant's wallet balances)
- Candle (shared across tenants, not tenant-specific)

### Future Plan: Multiple Users Per Tenant

The architecture supports future expansion to organization-level tenancy:
- **Organizations**: A tenant becomes an organization
- **User-Tenant Relationship**: Many-to-many (users can belong to multiple tenants)
- **Role per Tenant**: User can have different roles in different tenants
- **Data Isolation**: Remains at tenant level (TenantId filtering)

### Why This Approach?
- **Simplicity**: Single database, straightforward deployment
- **Cost-effective**: No per-tenant database overhead
- **Scalable**: Proven pattern for SaaS applications
- **Flexible**: Easy to add multi-user support later
- **PostgreSQL RLS**: Can be added for additional security layer if needed

---

## Testing & Quality

### Test Projects
- `tests/LaBot.Domain.Tests/` - Domain entity and business logic tests
- `tests/LaBot.Application.Tests/` - Application service tests
- `tests/LaBot.Infrastructure.Tests/` - Data access and integration tests
- `tests/LaBot.Integration.Tests/` - End-to-end integration tests

### Running Tests
```bash
# All tests
dotnet test

# With coverage (requires coverlet)
dotnet test /p:CollectCoverage=true

# Specific test project
dotnet test tests/LaBot.Domain.Tests/
```

---

## Deployment

For production deployment to Ubuntu 24.04:

1. **Read**: [DEPLOYMENT.md](DEPLOYMENT.md) - Complete deployment runbook
2. **Setup Exchange SDKs**: [VENDOR_SETUP.md](VENDOR_SETUP.md)
3. **Optional n8n**: [N8N_SETUP.md](N8N_SETUP.md)

**Key deployment components:**
- systemd services (labot-web, labot-api, labot-worker)
- Nginx reverse proxy with SSL (Certbot)
- PostgreSQL database
- Environment variables for secrets

---

## Common Tasks

### Add a New Migration
```bash
cd src/LaBot.Infrastructure
dotnet ef migrations add YourMigrationName --startup-project ../LaBot.Web/LaBot.Web.csproj
dotnet ef database update --startup-project ../LaBot.Web/LaBot.Web.csproj
```

### Add a New Exchange Adapter
1. Create new project: `src/LaBot.Exchanges.YourExchange/`
2. Implement `IExchangeAdapter` from `LaBot.Exchanges.Core`
3. Vendor exchange SDK if needed (see [VENDOR_SETUP.md](VENDOR_SETUP.md))
4. Register in dependency injection container

### Add a New Trading Strategy
1. Define strategy interface in `LaBot.Application/`
2. Implement in `LaBot.Worker/`
3. Register in Worker's service collection
4. Bot engine will pick up and execute

### View Application Logs (Production)
```bash
# Web logs
sudo journalctl -u labot-web -f

# API logs
sudo journalctl -u labot-api -f

# Worker logs
sudo journalctl -u labot-worker -f
```

---

## Getting Help

- **Documentation**: Start with `docs/README.md`
- **Issues**: Check existing issues or create a new one
- **Code Questions**: Review [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Development Checklist**: See [CHECKLIST.md](CHECKLIST.md) for systematic development workflow

---

**Last Updated**: 2026-02-06
