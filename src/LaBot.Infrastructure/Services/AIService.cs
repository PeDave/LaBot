using LaBot.Application.Interfaces;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using System.Text;
using System.Text.Json;

namespace LaBot.Infrastructure.Services;

public class AIService : IAIService
{
    private readonly ILogger<AIService> _logger;
    private readonly IConfiguration _configuration;
    private readonly HttpClient _httpClient;
    private readonly string _provider;

    public AIService(ILogger<AIService> logger, IConfiguration configuration, HttpClient httpClient)
    {
        _logger = logger;
        _configuration = configuration;
        _httpClient = httpClient;
        _provider = _configuration["AI:Provider"] ?? "OpenAI";
    }

    public async Task<string> GenerateCompletionAsync(string prompt, CancellationToken cancellationToken = default)
    {
        try
        {
            if (_provider == "OpenAI")
            {
                return await GenerateOpenAICompletionAsync(prompt, cancellationToken);
            }
            else if (_provider == "Azure")
            {
                return await GenerateAzureOpenAICompletionAsync(prompt, cancellationToken);
            }
            else
            {
                _logger.LogWarning("Unknown AI provider: {Provider}", _provider);
                return "AI provider not configured";
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating AI completion");
            throw;
        }
    }

    public async Task<MarketAnalysisResult> AnalyzeMarketAsync(MarketAnalysisRequest request, CancellationToken cancellationToken = default)
    {
        var prompt = $@"Analyze the following cryptocurrency market data and provide trading insights:

Symbol: {request.Symbol}
Current Price: ${request.CurrentPrice}
Additional Context: {request.AdditionalContext}

Please provide:
1. Market analysis
2. Trading recommendation (BUY/SELL/HOLD)
3. Confidence score (0-1)

Format your response as a structured analysis.";

        var analysis = await GenerateCompletionAsync(prompt, cancellationToken);

        // Simple parsing - in production, use structured output
        return new MarketAnalysisResult(
            Symbol: request.Symbol,
            Analysis: analysis,
            Recommendation: "HOLD", // Parse from AI response
            ConfidenceScore: 0.7m // Parse from AI response
        );
    }

    private async Task<string> GenerateOpenAICompletionAsync(string prompt, CancellationToken cancellationToken)
    {
        var apiKey = _configuration["AI:OpenAI:ApiKey"];
        if (string.IsNullOrEmpty(apiKey))
        {
            _logger.LogWarning("OpenAI API key not configured");
            return "OpenAI API key not configured. Please set AI:OpenAI:ApiKey in configuration.";
        }

        var endpoint = _configuration["AI:OpenAI:Endpoint"] ?? "https://api.openai.com/v1";
        var model = _configuration["AI:OpenAI:Model"] ?? "gpt-4";

        var requestBody = new
        {
            model = model,
            messages = new[]
            {
                new { role = "system", content = "You are a helpful cryptocurrency trading assistant." },
                new { role = "user", content = prompt }
            },
            max_tokens = 500,
            temperature = 0.7
        };

        var json = JsonSerializer.Serialize(requestBody);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        _httpClient.DefaultRequestHeaders.Clear();
        _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {apiKey}");

        var response = await _httpClient.PostAsync($"{endpoint}/chat/completions", content, cancellationToken);

        if (!response.IsSuccessStatusCode)
        {
            var errorContent = await response.Content.ReadAsStringAsync(cancellationToken);
            _logger.LogError("OpenAI API error: {StatusCode} - {Error}", response.StatusCode, errorContent);
            return $"AI service temporarily unavailable (Status: {response.StatusCode})";
        }

        var responseJson = await response.Content.ReadAsStringAsync(cancellationToken);
        using var doc = JsonDocument.Parse(responseJson);
        var completion = doc.RootElement
            .GetProperty("choices")[0]
            .GetProperty("message")
            .GetProperty("content")
            .GetString();

        return completion ?? "No response generated";
    }

    private async Task<string> GenerateAzureOpenAICompletionAsync(string prompt, CancellationToken cancellationToken)
    {
        var apiKey = _configuration["AI:Azure:ApiKey"];
        var endpoint = _configuration["AI:Azure:Endpoint"];
        var deploymentName = _configuration["AI:Azure:DeploymentName"];

        if (string.IsNullOrEmpty(apiKey) || string.IsNullOrEmpty(endpoint) || string.IsNullOrEmpty(deploymentName))
        {
            _logger.LogWarning("Azure OpenAI not fully configured");
            return "Azure OpenAI not configured. Please set AI:Azure:ApiKey, Endpoint, and DeploymentName.";
        }

        var requestBody = new
        {
            messages = new[]
            {
                new { role = "system", content = "You are a helpful cryptocurrency trading assistant." },
                new { role = "user", content = prompt }
            },
            max_tokens = 500,
            temperature = 0.7
        };

        var json = JsonSerializer.Serialize(requestBody);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        _httpClient.DefaultRequestHeaders.Clear();
        _httpClient.DefaultRequestHeaders.Add("api-key", apiKey);

        var url = $"{endpoint}/openai/deployments/{deploymentName}/chat/completions?api-version=2024-02-15-preview";
        var response = await _httpClient.PostAsync(url, content, cancellationToken);

        if (!response.IsSuccessStatusCode)
        {
            var errorContent = await response.Content.ReadAsStringAsync(cancellationToken);
            _logger.LogError("Azure OpenAI API error: {StatusCode} - {Error}", response.StatusCode, errorContent);
            return $"AI service temporarily unavailable (Status: {response.StatusCode})";
        }

        var responseJson = await response.Content.ReadAsStringAsync(cancellationToken);
        using var doc = JsonDocument.Parse(responseJson);
        var completion = doc.RootElement
            .GetProperty("choices")[0]
            .GetProperty("message")
            .GetProperty("content")
            .GetString();

        return completion ?? "No response generated";
    }
}
