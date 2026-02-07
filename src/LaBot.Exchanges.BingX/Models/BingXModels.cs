using System.Text.Json.Serialization;

namespace LaBot.Exchanges.BingX.Models;

public class BingXResponse<T>
{
    [JsonPropertyName("code")]
    public int Code { get; set; }

    [JsonPropertyName("msg")]
    public string Message { get; set; } = string.Empty;

    [JsonPropertyName("data")]
    public T? Data { get; set; }
}

public class BingXBalanceData
{
    [JsonPropertyName("balances")]
    public List<BingXBalance> Balances { get; set; } = new();
}

public class BingXBalance
{
    [JsonPropertyName("asset")]
    public string Asset { get; set; } = string.Empty;

    [JsonPropertyName("free")]
    public string Free { get; set; } = "0";

    [JsonPropertyName("locked")]
    public string Locked { get; set; } = "0";
}

public class BingXSymbol
{
    [JsonPropertyName("symbol")]
    public string Symbol { get; set; } = string.Empty;

    [JsonPropertyName("asset")]
    public string Asset { get; set; } = string.Empty;

    [JsonPropertyName("currency")]
    public string Currency { get; set; } = string.Empty;

    [JsonPropertyName("minQty")]
    public string MinQty { get; set; } = "0";

    [JsonPropertyName("maxQty")]
    public string MaxQty { get; set; } = "0";

    [JsonPropertyName("status")]
    public int Status { get; set; }
}

public class BingXSymbolsData
{
    [JsonPropertyName("symbols")]
    public List<BingXSymbol> Symbols { get; set; } = new();
}
