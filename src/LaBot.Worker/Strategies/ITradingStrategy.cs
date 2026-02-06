using LaBot.Exchanges.Core.Interfaces;
using LaBot.Exchanges.Core.Models;

namespace LaBot.Worker.Strategies;

public interface ITradingStrategy
{
    string Name { get; }
    Task<Signal?> GenerateSignalAsync(IExchangeAdapter exchange, string symbol, CancellationToken cancellationToken = default);
}

public class Signal
{
    public string Symbol { get; set; } = string.Empty;
    public OrderSide Side { get; set; }
    public decimal Quantity { get; set; }
    public decimal? Price { get; set; }
    public string Reason { get; set; } = string.Empty;
}
