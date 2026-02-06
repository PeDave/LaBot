using LaBot.Domain.Enums;

namespace LaBot.Domain.Entities;

public class Candle
{
    public Guid Id { get; set; }
    public string Symbol { get; set; } = string.Empty; // BTC/USDT, ETH/USDT
    public string ExchangeName { get; set; } = string.Empty;
    public CandleInterval Interval { get; set; }
    public DateTime OpenTime { get; set; }
    public DateTime CloseTime { get; set; }
    public decimal Open { get; set; }
    public decimal High { get; set; }
    public decimal Low { get; set; }
    public decimal Close { get; set; }
    public decimal Volume { get; set; }
    public DateTime CreatedAt { get; set; }
}
