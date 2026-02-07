using LaBot.Application.Interfaces;
using LaBot.Infrastructure.Services;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Moq;
using Moq.Protected;
using System.Net;
using Xunit;

namespace LaBot.Infrastructure.Tests;

public class AIServiceTests
{
    [Fact]
    public void AIService_Constructor_InitializesCorrectly()
    {
        // Arrange
        var logger = new Mock<ILogger<AIService>>();
        var configuration = CreateConfiguration("OpenAI");
        var httpClient = new HttpClient();

        // Act
        var service = new AIService(logger.Object, configuration, httpClient);

        // Assert
        Assert.NotNull(service);
    }

    [Fact]
    public async Task GenerateCompletion_NoApiKey_ReturnsConfigMessage()
    {
        // Arrange
        var logger = new Mock<ILogger<AIService>>();
        var configuration = CreateConfiguration("OpenAI", includeApiKey: false);
        var httpClient = new HttpClient();
        var service = new AIService(logger.Object, configuration, httpClient);

        // Act
        var result = await service.GenerateCompletionAsync("test prompt");

        // Assert
        Assert.Contains("not configured", result, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public async Task AnalyzeMarket_ValidRequest_ReturnsResult()
    {
        // Arrange
        var logger = new Mock<ILogger<AIService>>();
        var configuration = CreateConfiguration("OpenAI", includeApiKey: false);
        var httpClient = new HttpClient();
        var service = new AIService(logger.Object, configuration, httpClient);

        var request = new MarketAnalysisRequest(
            Symbol: "BTC/USDT",
            CurrentPrice: 50000m,
            AdditionalContext: "Test analysis"
        );

        // Act
        var result = await service.AnalyzeMarketAsync(request);

        // Assert
        Assert.NotNull(result);
        Assert.Equal("BTC/USDT", result.Symbol);
        Assert.NotNull(result.Analysis);
        Assert.NotNull(result.Recommendation);
    }

    [Theory]
    [InlineData("OpenAI")]
    [InlineData("Azure")]
    public void AIService_SupportsMultipleProviders(string provider)
    {
        // Arrange
        var logger = new Mock<ILogger<AIService>>();
        var configuration = CreateConfiguration(provider);
        var httpClient = new HttpClient();

        // Act
        var service = new AIService(logger.Object, configuration, httpClient);

        // Assert
        Assert.NotNull(service);
    }

    [Fact]
    public async Task GenerateCompletion_HttpError_HandlesGracefully()
    {
        // Arrange
        var logger = new Mock<ILogger<AIService>>();
        var configuration = CreateConfiguration("OpenAI", includeApiKey: true);
        
        var mockHandler = new Mock<HttpMessageHandler>();
        mockHandler.Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>()
            )
            .ReturnsAsync(new HttpResponseMessage
            {
                StatusCode = HttpStatusCode.Unauthorized,
                Content = new StringContent("Invalid API key")
            });

        var httpClient = new HttpClient(mockHandler.Object);
        var service = new AIService(logger.Object, configuration, httpClient);

        // Act
        var result = await service.GenerateCompletionAsync("test prompt");

        // Assert
        Assert.Contains("unavailable", result, StringComparison.OrdinalIgnoreCase);
    }

    private static IConfiguration CreateConfiguration(string provider, bool includeApiKey = false)
    {
        var config = new Dictionary<string, string>
        {
            ["AI:Provider"] = provider,
            ["AI:OpenAI:ApiKey"] = includeApiKey ? "test_key_123" : "",
            ["AI:OpenAI:Model"] = "gpt-4",
            ["AI:OpenAI:Endpoint"] = "https://api.openai.com/v1",
            ["AI:Azure:ApiKey"] = includeApiKey ? "test_azure_key" : "",
            ["AI:Azure:Endpoint"] = "https://test.openai.azure.com",
            ["AI:Azure:DeploymentName"] = "test-deployment"
        };

        return new ConfigurationBuilder()
            .AddInMemoryCollection(config!)
            .Build();
    }
}
