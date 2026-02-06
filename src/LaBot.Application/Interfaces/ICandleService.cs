using LaBot.Domain.Entities;
using LaBot.Domain.Enums;

namespace LaBot.Application.Interfaces;

public interface ICandleService
{
    Task<List<Candle>> GetCandlesAsync(string symbol, string exchangeName, CandleInterval interval, DateTime? startTime = null, DateTime? endTime = null, CancellationToken cancellationToken = default);
    Task SaveCandlesAsync(List<Candle> candles, CancellationToken cancellationToken = default);
}
