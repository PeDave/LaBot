namespace LaBot.Exchanges.BingX.Configuration;

public class BingXOptions
{
    public const string SectionName = "BingX";

    public string ApiKey { get; set; } = string.Empty;
    public string ApiSecret { get; set; } = string.Empty;
    public string BaseUrl { get; set; } = "https://open-api.bingx.com";
    public int RecvWindow { get; set; } = 5000;
    public int PollIntervalSeconds { get; set; } = 10;
}
