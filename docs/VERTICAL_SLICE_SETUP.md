# LaBot Setup Guide - Vertical Slice Implementation

This guide walks you through setting up and testing the first vertical slice implementation of LaBot.

## What's Implemented

The vertical slice includes:
- ✅ **Authentication**: JWT token generation with role-based access
- ✅ **Stripe Integration**: Webhook handling with signature verification and subscription management
- ✅ **AI Integration**: OpenAI/Azure OpenAI support for market analysis
- ✅ **n8n Integration**: Sample workflows for trading signals
- ✅ **Complete API Layer**: RESTful endpoints with proper DI and configuration
- ✅ **Tests**: 21 passing tests covering critical functionality

## Prerequisites

- .NET 8 SDK
- PostgreSQL 14+
- (Optional) OpenAI or Azure OpenAI API key for AI features
- (Optional) Stripe account for subscription testing
- (Optional) n8n installation for workflow automation

## Quick Start

### 1. Clone and Build

```bash
git clone https://github.com/PeDave/LaBot.git
cd LaBot
git checkout copilot/implement-first-vertical-slice
dotnet restore
dotnet build --configuration Release
```

### 2. Database Setup

```bash
# Create PostgreSQL database
sudo -u postgres psql
CREATE DATABASE labot;
CREATE USER labot WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE labot TO labot;
\q

# Run EF Core migrations
cd src/LaBot.Infrastructure
dotnet ef database update --startup-project ../LaBot.Web/LaBot.Web.csproj
```

### 3. Configuration

#### Option A: User Secrets (Recommended for Development)

```bash
# For LaBot.Web
cd src/LaBot.Web
dotnet user-secrets init
dotnet user-secrets set "ConnectionStrings:DefaultConnection" "Host=localhost;Database=labot;Username=labot;Password=your_secure_password"
dotnet user-secrets set "Jwt:SecretKey" "YourSuperSecretJWTKeyThatIsAtLeast32CharactersLong!"
dotnet user-secrets set "Stripe:SecretKey" "sk_test_your_stripe_secret_key"
dotnet user-secrets set "Stripe:WebhookSecret" "whsec_your_webhook_secret"
dotnet user-secrets set "AI:OpenAI:ApiKey" "sk-your_openai_api_key"

# For LaBot.Api
cd ../LaBot.Api
dotnet user-secrets init
dotnet user-secrets set "ConnectionStrings:DefaultConnection" "Host=localhost;Database=labot;Username=labot;Password=your_secure_password"
dotnet user-secrets set "Jwt:SecretKey" "YourSuperSecretJWTKeyThatIsAtLeast32CharactersLong!"
dotnet user-secrets set "Stripe:SecretKey" "sk_test_your_stripe_secret_key"
dotnet user-secrets set "Stripe:WebhookSecret" "whsec_your_webhook_secret"
dotnet user-secrets set "AI:OpenAI:ApiKey" "sk-your_openai_api_key"
```

#### Option B: Environment Variables

```bash
export ConnectionStrings__DefaultConnection="Host=localhost;Database=labot;Username=labot;Password=your_secure_password"
export Jwt__SecretKey="YourSuperSecretJWTKeyThatIsAtLeast32CharactersLong!"
export Stripe__SecretKey="sk_test_your_stripe_secret_key"
export Stripe__WebhookSecret="whsec_your_webhook_secret"
export AI__OpenAI__ApiKey="sk-your_openai_api_key"
```

#### Option C: appsettings.Development.json (Not recommended for secrets)

Copy `appsettings.secrets.json.example` to `src/LaBot.Api/appsettings.Development.json` and fill in your values.

### 4. Run the Applications

Open three terminal windows:

**Terminal 1 - Web Dashboard:**
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
# Swagger: https://localhost:5001/swagger
```

**Terminal 3 - Worker (Optional):**
```bash
cd src/LaBot.Worker
dotnet run
```

### 5. Test the Implementation

#### A. Authentication (JWT Tokens)

The JWT token service is configured but not yet exposed via API endpoints. It's used internally and tested via unit tests.

```bash
# Run authentication tests
dotnet test tests/LaBot.Application.Tests/ --filter TokenServiceTests
```

#### B. AI Service

```bash
# Test AI endpoints (requires API key configured)
curl -X POST https://localhost:5001/api/AI/completion \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Analyze BTC market trends"}'

# Test market analysis
curl -X POST https://localhost:5001/api/AI/analyze-market \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC/USDT",
    "currentPrice": 50000,
    "additionalContext": "Recent 20% price increase"
  }'

# Health check
curl https://localhost:5001/api/AI/health
```

#### C. Stripe Webhooks

To test Stripe webhooks locally, use Stripe CLI:

```bash
# Install Stripe CLI
# https://stripe.com/docs/stripe-cli

# Forward webhooks to local endpoint
stripe listen --forward-to https://localhost:5001/api/StripeWebhook

# In another terminal, trigger test events
stripe trigger checkout.session.completed
stripe trigger customer.subscription.created
```

#### D. n8n Integration

1. Import the workflow from `docs/n8n-workflows/trading-signal-workflow.json`
2. Configure the webhook URL to point to your API
3. Test sending signals:

```bash
curl -X POST https://localhost:5001/api/N8nWebhook/signal \
  -H "Content-Type: application/json" \
  -d '{
    "signalId": "test-123",
    "symbol": "BTC/USDT",
    "action": "BUY",
    "price": 50000,
    "quantity": 0.1
  }'
```

### 6. Run All Tests

```bash
# Run all tests
dotnet test

# Expected output:
# Total tests: 21
# Passed: 21
# Failed: 0
```

## Testing Checklist

Use this checklist to verify the vertical slice:

- [ ] Database connection successful
- [ ] Web dashboard loads at https://localhost:5000
- [ ] API Swagger UI loads at https://localhost:5001/swagger
- [ ] All 21 tests pass
- [ ] AI health check returns 200 OK
- [ ] AI completion endpoint works (with API key)
- [ ] n8n signal webhook accepts payloads
- [ ] Stripe webhook signature verification works

## Configuration Reference

### Required Configurations

| Setting | Description | Example |
|---------|-------------|---------|
| `ConnectionStrings:DefaultConnection` | PostgreSQL connection | `Host=localhost;Database=labot;...` |
| `Jwt:SecretKey` | JWT token signing key (min 32 chars) | `Your...Key!` |
| `Stripe:SecretKey` | Stripe API secret key | `sk_test_...` |
| `Stripe:WebhookSecret` | Stripe webhook signature key | `whsec_...` |

### Optional Configurations

| Setting | Description | Default |
|---------|-------------|---------|
| `AI:Provider` | AI provider (OpenAI/Azure) | `OpenAI` |
| `AI:OpenAI:ApiKey` | OpenAI API key | (none) |
| `AI:OpenAI:Model` | OpenAI model | `gpt-4` |
| `AI:Azure:ApiKey` | Azure OpenAI key | (none) |
| `AI:Azure:Endpoint` | Azure endpoint URL | (none) |
| `Jwt:Issuer` | JWT issuer | `LaBot` |
| `Jwt:Audience` | JWT audience | `LaBot` |
| `Jwt:ExpirationMinutes` | Token lifetime | `60` |

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -h localhost -U labot -d labot
```

### JWT Secret Key Error

If you see "JWT Secret Key must be configured", ensure you've set `Jwt:SecretKey` in user secrets or environment variables.

### AI Service Returns "Not Configured"

This is expected if you haven't provided an API key. The service will return a descriptive message. Add the key to enable AI features.

### Stripe Webhook Signature Fails

Ensure the `Stripe:WebhookSecret` matches your Stripe webhook configuration. Use Stripe CLI to test locally.

## Next Steps

After verifying the vertical slice:

1. Configure production secrets in deployment environment
2. Set up Stripe products and price IDs
3. Configure AI provider for production use
4. Deploy to staging environment
5. Test end-to-end subscription flow
6. Import n8n workflows
7. Configure monitoring and logging

## Security Notes

- ⚠️ Never commit secrets to the repository
- ⚠️ Use user secrets or environment variables for development
- ⚠️ JWT secret must be at least 32 characters
- ⚠️ CORS is configured for development (any origin) - restrict in production
- ⚠️ Stripe price ID mapping is simplified - use configuration in production
- ✅ All tests include security validations
- ✅ CodeQL scan shows 0 vulnerabilities

## Support

For issues or questions:
- Check existing issues: https://github.com/PeDave/LaBot/issues
- Review documentation: `docs/`
- Contact maintainer

## License

Proprietary - All rights reserved.
