namespace LaBot.Domain.ValueObjects;

public record SymbolInfo(string BaseAsset, string QuoteAsset)
{
    public static SymbolInfo Parse(string symbol)
    {
        var parts = symbol.Split('/');
        if (parts.Length != 2)
        {
            throw new ArgumentException($"Invalid symbol format: {symbol}. Expected format: BTC/USDT");
        }

        return new SymbolInfo(parts[0], parts[1]);
    }

    public override string ToString() => $"{BaseAsset}/{QuoteAsset}";
}
