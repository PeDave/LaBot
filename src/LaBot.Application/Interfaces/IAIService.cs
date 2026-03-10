namespace LaBot.Application.Interfaces;

public interface IAIService
{
    /// <summary>
    /// Generates a text completion based on the provided prompt
    /// </summary>
    Task<string> GenerateCompletionAsync(string prompt, CancellationToken cancellationToken = default);

    /// <summary>
    /// Analyzes market data and provides trading insights
    /// </summary>
    Task<MarketAnalysisResult> AnalyzeMarketAsync(MarketAnalysisRequest request, CancellationToken cancellationToken = default);
}

public record MarketAnalysisRequest(
    string Symbol,
    decimal CurrentPrice,
    string AdditionalContext
);

public record MarketAnalysisResult(
    string Symbol,
    string Analysis,
    string Recommendation,
    decimal ConfidenceScore
);
