namespace LaBot.Exchanges.Core.Models;

public enum OrderSide
{
    Buy,
    Sell
}

public enum OrderStatus
{
    New,
    PartiallyFilled,
    Filled,
    Canceled,
    Rejected,
    Expired
}

public record OrderResult(
    string OrderId,
    string Symbol,
    OrderSide Side,
    decimal Quantity,
    decimal? Price,
    OrderStatus Status,
    DateTime Timestamp
);

public record Balance(
    string Asset,
    decimal Total,
    decimal Available,
    decimal Locked
);

public record Ticker(
    string Symbol,
    decimal LastPrice,
    decimal BidPrice,
    decimal AskPrice,
    decimal Volume24h,
    DateTime Timestamp
);

public record Candle(
    DateTime OpenTime,
    DateTime CloseTime,
    decimal Open,
    decimal High,
    decimal Low,
    decimal Close,
    decimal Volume
);

public record Symbol(
    string Name,
    string BaseAsset,
    string QuoteAsset,
    decimal MinQuantity,
    decimal MaxQuantity,
    decimal QuantityStep,
    decimal MinPrice,
    decimal MaxPrice,
    decimal PriceStep,
    bool IsActive
);
