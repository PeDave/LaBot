namespace LaBot.Exchanges.Core.Interfaces;

public interface IExchangeWebSocketClient
{
    Task SubscribeToTickerAsync(string symbol, Action<object> onUpdate, CancellationToken cancellationToken = default);
    Task SubscribeToCandlesAsync(string symbol, string interval, Action<object> onUpdate, CancellationToken cancellationToken = default);
    Task UnsubscribeAsync(string symbol, CancellationToken cancellationToken = default);
    Task DisconnectAsync(CancellationToken cancellationToken = default);
}
