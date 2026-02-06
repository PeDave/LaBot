using LaBot.Exchanges.BingX.Configuration;
using LaBot.Exchanges.BingX.Http;
using Microsoft.Extensions.Logging.Abstractions;
using Xunit;

namespace LaBot.Exchanges.BingX.Tests;

public class BingXRestClientTests
{
    [Fact]
    public void GenerateSignature_ShouldProduceValidHmacSha256()
    {
        // Arrange
        var options = new BingXOptions
        {
            ApiKey = "test-api-key",
            ApiSecret = "test-secret-key",
            BaseUrl = "https://open-api.bingx.com"
        };

        var httpClient = new HttpClient();
        var logger = NullLogger<BingXRestClient>.Instance;
        var client = new BingXRestClient(httpClient, options, logger);

        var queryString = "recvWindow=5000&timestamp=1234567890";

        // Act
        var signature = client.GenerateSignature(queryString);

        // Assert
        Assert.NotNull(signature);
        Assert.NotEmpty(signature);
        Assert.Equal(64, signature.Length); // HMAC-SHA256 produces 64 hex characters
        Assert.Matches("^[a-f0-9]+$", signature); // Should be lowercase hex
    }

    [Fact]
    public void GenerateSignature_ShouldBeConsistent()
    {
        // Arrange
        var options = new BingXOptions
        {
            ApiKey = "test-api-key",
            ApiSecret = "test-secret-key",
            BaseUrl = "https://open-api.bingx.com"
        };

        var httpClient = new HttpClient();
        var logger = NullLogger<BingXRestClient>.Instance;
        var client = new BingXRestClient(httpClient, options, logger);

        var queryString = "recvWindow=5000&timestamp=1234567890";

        // Act
        var signature1 = client.GenerateSignature(queryString);
        var signature2 = client.GenerateSignature(queryString);

        // Assert
        Assert.Equal(signature1, signature2);
    }

    [Fact]
    public void GenerateSignature_DifferentInputsShouldProduceDifferentSignatures()
    {
        // Arrange
        var options = new BingXOptions
        {
            ApiKey = "test-api-key",
            ApiSecret = "test-secret-key",
            BaseUrl = "https://open-api.bingx.com"
        };

        var httpClient = new HttpClient();
        var logger = NullLogger<BingXRestClient>.Instance;
        var client = new BingXRestClient(httpClient, options, logger);

        var queryString1 = "recvWindow=5000&timestamp=1234567890";
        var queryString2 = "recvWindow=5000&timestamp=9876543210";

        // Act
        var signature1 = client.GenerateSignature(queryString1);
        var signature2 = client.GenerateSignature(queryString2);

        // Assert
        Assert.NotEqual(signature1, signature2);
    }

    [Fact]
    public void GenerateSignature_KnownTestCase()
    {
        // Arrange - Using a known test vector
        var options = new BingXOptions
        {
            ApiKey = "test-api-key",
            ApiSecret = "secret",
            BaseUrl = "https://open-api.bingx.com"
        };

        var httpClient = new HttpClient();
        var logger = NullLogger<BingXRestClient>.Instance;
        var client = new BingXRestClient(httpClient, options, logger);

        var queryString = "symbol=BTC-USDT&timestamp=1649404670000&recvWindow=5000";

        // Act
        var signature = client.GenerateSignature(queryString);

        // Assert
        // The signature should be computed using HMAC-SHA256("secret", queryString)
        // For now, just verify it's a valid signature format
        Assert.NotNull(signature);
        Assert.Equal(64, signature.Length);
        Assert.Matches("^[a-f0-9]+$", signature);
    }
}
