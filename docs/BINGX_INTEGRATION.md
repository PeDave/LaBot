# BingX Spot API Integration

This document describes the BingX Spot API v3 integration for the LaBot Worker service.

## Features

- **Balance Polling**: Periodic polling of account balances (all assets) with configurable interval
- **Symbol/Market Fetching**: Fetch spot symbol list at startup or periodically
- **Environment-based Configuration**: Credentials loaded from environment variables for security
- **Error Handling**: Graceful error handling without crashing the service
- **Structured Logging**: Comprehensive logging of API calls and results

## Configuration

### Environment Variables (Recommended)

Set the following environment variables to configure the BingX integration:

```bash
# Required
export BINGX_API_KEY="your-api-key"
export BINGX_API_SECRET="your-api-secret"

# Optional (with defaults)
export BINGX_BASE_URL="https://open-api.bingx.com"  # Default
export BINGX_RECV_WINDOW="5000"                      # Default: 5000ms
export BINGX_POLL_INTERVAL_SECONDS="10"             # Default: 10 seconds
```

### Configuration File

Alternatively, you can configure in `appsettings.json`:

```json
{
  "BingX": {
    "ApiKey": "your-api-key",
    "ApiSecret": "your-api-secret",
    "BaseUrl": "https://open-api.bingx.com",
    "RecvWindow": 5000,
    "PollIntervalSeconds": 10
  }
}
```

**Note**: Environment variables take precedence over configuration file settings.

## Running the Worker

### With Environment Variables

```bash
cd src/LaBot.Worker
export BINGX_API_KEY="your-api-key"
export BINGX_API_SECRET="your-api-secret"
dotnet run
```

### Behavior

1. **On Startup**:
   - Worker checks if `BINGX_API_KEY` is configured
   - If configured, `BingXBalancePoller` background service starts
   - Fetches spot symbols once at startup and logs the count

2. **During Runtime**:
   - Polls account balances every N seconds (configurable)
   - Logs balance summary (total, available, locked)
   - Logs individual asset balances (up to 10 assets in detail)
   - Handles API errors gracefully without crashing

3. **On Shutdown**:
   - Honors cancellation token
   - Cleanly stops the polling loop

## API Endpoints Used

Based on [BingX API v3 Documentation](https://bingx-api.github.io/docs-v3/#/en/info):

### Public Endpoints
- **GET /openApi/spot/v1/common/symbols** - Fetch spot trading symbols

### Private Endpoints (Requires Authentication)
- **GET /openApi/spot/v1/account/balance** - Get account balances

## Authentication

The integration uses HMAC-SHA256 signature authentication:

1. Query parameters are sorted alphabetically
2. A signature is generated using HMAC-SHA256(secretKey, queryString)
3. The signature is appended to the query string
4. API key is sent in the `X-BX-APIKEY` header

## Logging Examples

### Successful Symbol Fetch
```
info: LaBot.Worker.Services.BingXBalancePoller[0]
      Successfully fetched 456 symbols from BingX
```

### Successful Balance Fetch
```
info: LaBot.Worker.Services.BingXBalancePoller[0]
      Successfully fetched 5 balances from BingX
info: LaBot.Worker.Services.BingXBalancePoller[0]
      Balance summary - Total: 1234.56, Available: 1000.00, Locked: 234.56
```

### Error Handling
```
fail: LaBot.Exchanges.BingX.Adapters.BingXAdapter[0]
      Failed to fetch balances: 100001 Invalid API key
```

## Security Considerations

- ✅ API credentials are loaded from environment variables (not committed to source)
- ✅ Secrets are not logged
- ✅ HTTPS is enforced for API communication
- ✅ Request signatures prevent tampering

## Testing

Unit tests are included for signature generation and query building:

```bash
cd tests/LaBot.Exchanges.BingX.Tests
dotnet test
```

## Troubleshooting

### BingXBalancePoller doesn't start
- Ensure `BINGX_API_KEY` environment variable is set
- Check Worker logs for startup messages

### API returns 100001 error
- Invalid API key - verify your credentials
- Ensure API key has spot trading permissions

### API returns signature errors
- Verify `BINGX_API_SECRET` is correct
- Check system time is synchronized (signatures use timestamps)

### Network errors
- Verify internet connectivity
- Check firewall settings
- Ensure `BINGX_BASE_URL` is accessible
