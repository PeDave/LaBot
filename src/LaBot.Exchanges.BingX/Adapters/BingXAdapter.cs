using LaBot.Exchanges.BingX.Http;
using LaBot.Exchanges.BingX.Models;
using LaBot.Exchanges.Core.Interfaces;
using LaBot.Exchanges.Core.Models;
using Microsoft.Extensions.Logging;

namespace LaBot.Exchanges.BingX.Adapters;

public class BingXAdapter : IExchangeAdapter
{
    private readonly BingXRestClient _restClient;
    private readonly ILogger<BingXAdapter> _logger;

    public string ExchangeName => "BingX";

    public BingXAdapter(BingXRestClient restClient, ILogger<BingXAdapter> logger)
    {
        _restClient = restClient;
        _logger = logger;
    }

    public async Task<OrderResult> PlaceMarketOrderAsync(string symbol, OrderSide side, decimal quantity, CancellationToken cancellationToken = default)
    {
        // TODO: Implement using vendored BingX.Net SDK
        await Task.Delay(100, cancellationToken);

        return new OrderResult(
            OrderId: Guid.NewGuid().ToString(),
            Symbol: symbol,
            Side: side,
            Quantity: quantity,
            Price: null,
            Status: OrderStatus.New,
            Timestamp: DateTime.UtcNow
        );
    }

    public async Task<OrderResult> PlaceLimitOrderAsync(string symbol, OrderSide side, decimal quantity, decimal price, CancellationToken cancellationToken = default)
    {
        // TODO: Implement using vendored BingX.Net SDK
        await Task.Delay(100, cancellationToken);

        return new OrderResult(
            OrderId: Guid.NewGuid().ToString(),
            Symbol: symbol,
            Side: side,
            Quantity: quantity,
            Price: price,
            Status: OrderStatus.New,
            Timestamp: DateTime.UtcNow
        );
    }

    public async Task<OrderResult> CancelOrderAsync(string symbol, string orderId, CancellationToken cancellationToken = default)
    {
        // TODO: Implement using vendored BingX.Net SDK
        await Task.Delay(100, cancellationToken);

        return new OrderResult(
            OrderId: orderId,
            Symbol: symbol,
            Side: OrderSide.Buy,
            Quantity: 0,
            Price: null,
            Status: OrderStatus.Canceled,
            Timestamp: DateTime.UtcNow
        );
    }

    public async Task<OrderStatus> GetOrderStatusAsync(string symbol, string orderId, CancellationToken cancellationToken = default)
    {
        // TODO: Implement using vendored BingX.Net SDK
        await Task.Delay(100, cancellationToken);
        return OrderStatus.New;
    }

    public async Task<Balance> GetBalanceAsync(string asset, CancellationToken cancellationToken = default)
    {
        var allBalances = await GetAllBalancesAsync(cancellationToken);
        var balance = allBalances.FirstOrDefault(b => b.Asset.Equals(asset, StringComparison.OrdinalIgnoreCase));
        return balance ?? new Balance(asset, 0, 0, 0);
    }

    public async Task<List<Balance>> GetAllBalancesAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            var response = await _restClient.GetAsync<BingXBalanceData>(
                "/openApi/spot/v1/account/balance",
                signed: true,
                cancellationToken: cancellationToken
            );

            if (response.Code != 0 || response.Data == null)
            {
                _logger.LogError("Failed to fetch balances: {Code} {Message}", response.Code, response.Message);
                return new List<Balance>();
            }

            var balances = response.Data.Balances
                .Select(b =>
                {
                    var free = decimal.TryParse(b.Free, out var freeValue) ? freeValue : 0;
                    var locked = decimal.TryParse(b.Locked, out var lockedValue) ? lockedValue : 0;
                    return new Balance(
                        Asset: b.Asset,
                        Total: free + locked,
                        Available: free,
                        Locked: locked
                    );
                })
                .Where(b => b.Total > 0 || b.Available > 0 || b.Locked > 0)
                .ToList();

            _logger.LogDebug("Fetched {Count} balances from BingX", balances.Count);
            return balances;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Exception fetching balances from BingX");
            return new List<Balance>();
        }
    }

    public async Task<List<Symbol>> GetSymbolsAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            var response = await _restClient.GetAsync<BingXSymbolsData>(
                "/openApi/spot/v1/common/symbols",
                signed: false,
                cancellationToken: cancellationToken
            );

            if (response.Code != 0 || response.Data == null)
            {
                _logger.LogError("Failed to fetch symbols: {Code} {Message}", response.Code, response.Message);
                return new List<Symbol>();
            }

            var symbols = response.Data.Symbols
                .Where(s => s.Status == 1) // Only active symbols
                .Select(s =>
                {
                    var minQty = decimal.TryParse(s.MinQty, out var minQtyValue) ? minQtyValue : 0;
                    var maxQty = decimal.TryParse(s.MaxQty, out var maxQtyValue) ? maxQtyValue : 0;
                    return new Symbol(
                        Name: s.Symbol,
                        BaseAsset: s.Asset,
                        QuoteAsset: s.Currency,
                        MinQuantity: minQty,
                        MaxQuantity: maxQty,
                        QuantityStep: 0.00000001m, // Default, would need more API details
                        MinPrice: 0, // Would need more API details
                        MaxPrice: 0, // Would need more API details
                        PriceStep: 0.01m, // Default, would need more API details
                        IsActive: s.Status == 1
                    );
                })
                .ToList();

            _logger.LogDebug("Fetched {Count} symbols from BingX", symbols.Count);
            return symbols;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Exception fetching symbols from BingX");
            return new List<Symbol>();
        }
    }

    public async Task<Ticker> GetTickerAsync(string symbol, CancellationToken cancellationToken = default)
    {
        // TODO: Implement using vendored BingX.Net SDK
        await Task.Delay(100, cancellationToken);

        return new Ticker(
            Symbol: symbol,
            LastPrice: 0,
            BidPrice: 0,
            AskPrice: 0,
            Volume24h: 0,
            Timestamp: DateTime.UtcNow
        );
    }

    public async Task<List<Candle>> GetCandlesAsync(string symbol, string interval, DateTime? startTime = null, DateTime? endTime = null, int? limit = null, CancellationToken cancellationToken = default)
    {
        // TODO: Implement using vendored BingX.Net SDK
        await Task.Delay(100, cancellationToken);
        return new List<Candle>();
    }
}
