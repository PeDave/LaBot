using LaBot.Exchanges.Core.Models;

namespace LaBot.Exchanges.Core.Interfaces;

public interface IExchangeAdapter
{
    string ExchangeName { get; }
    
    Task<OrderResult> PlaceMarketOrderAsync(string symbol, OrderSide side, decimal quantity, CancellationToken cancellationToken = default);
    Task<OrderResult> PlaceLimitOrderAsync(string symbol, OrderSide side, decimal quantity, decimal price, CancellationToken cancellationToken = default);
    Task<OrderResult> CancelOrderAsync(string symbol, string orderId, CancellationToken cancellationToken = default);
    Task<OrderStatus> GetOrderStatusAsync(string symbol, string orderId, CancellationToken cancellationToken = default);
    Task<Balance> GetBalanceAsync(string asset, CancellationToken cancellationToken = default);
    Task<List<Balance>> GetAllBalancesAsync(CancellationToken cancellationToken = default);
    Task<Ticker> GetTickerAsync(string symbol, CancellationToken cancellationToken = default);
    Task<List<Candle>> GetCandlesAsync(string symbol, string interval, DateTime? startTime = null, DateTime? endTime = null, int? limit = null, CancellationToken cancellationToken = default);
}
