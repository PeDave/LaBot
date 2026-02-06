using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using LaBot.Exchanges.BingX.Configuration;
using LaBot.Exchanges.BingX.Models;
using Microsoft.Extensions.Logging;

namespace LaBot.Exchanges.BingX.Http;

public class BingXRestClient
{
    private readonly HttpClient _httpClient;
    private readonly BingXOptions _options;
    private readonly ILogger<BingXRestClient> _logger;

    public BingXRestClient(HttpClient httpClient, BingXOptions options, ILogger<BingXRestClient> logger)
    {
        _httpClient = httpClient;
        _options = options;
        _logger = logger;
        _httpClient.BaseAddress = new Uri(_options.BaseUrl);
    }

    public async Task<BingXResponse<T>> GetAsync<T>(string endpoint, Dictionary<string, string>? parameters = null, bool signed = false, CancellationToken cancellationToken = default)
    {
        try
        {
            var queryString = BuildQueryString(parameters ?? new Dictionary<string, string>(), signed);
            var url = $"{endpoint}?{queryString}";

            _logger.LogDebug("BingX API request: {Method} {Url}", "GET", url);

            var request = new HttpRequestMessage(HttpMethod.Get, url);
            if (signed)
            {
                request.Headers.Add("X-BX-APIKEY", _options.ApiKey);
            }

            var response = await _httpClient.SendAsync(request, cancellationToken);
            var content = await response.Content.ReadAsStringAsync(cancellationToken);

            _logger.LogDebug("BingX API response: {StatusCode} {Content}", response.StatusCode, content);

            if (!response.IsSuccessStatusCode)
            {
                _logger.LogError("BingX API error: {StatusCode} {Content}", response.StatusCode, content);
                return new BingXResponse<T>
                {
                    Code = (int)response.StatusCode,
                    Message = $"HTTP {response.StatusCode}: {content}",
                    Data = default
                };
            }

            var result = JsonSerializer.Deserialize<BingXResponse<T>>(content);
            if (result == null)
            {
                _logger.LogError("Failed to deserialize BingX response");
                return new BingXResponse<T>
                {
                    Code = -1,
                    Message = "Failed to deserialize response",
                    Data = default
                };
            }

            if (result.Code != 0)
            {
                _logger.LogWarning("BingX API returned error code: {Code} {Message}", result.Code, result.Message);
            }

            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Exception calling BingX API: {Endpoint}", endpoint);
            return new BingXResponse<T>
            {
                Code = -1,
                Message = ex.Message,
                Data = default
            };
        }
    }

    private string BuildQueryString(Dictionary<string, string> parameters, bool signed)
    {
        if (signed)
        {
            var timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds().ToString();
            parameters["timestamp"] = timestamp;
            parameters["recvWindow"] = _options.RecvWindow.ToString();
        }

        // Sort parameters alphabetically for canonical form
        var sortedParams = parameters.OrderBy(p => p.Key).ToList();
        var queryString = string.Join("&", sortedParams.Select(p => $"{p.Key}={Uri.EscapeDataString(p.Value)}"));

        if (signed)
        {
            var signature = GenerateSignature(queryString);
            queryString += $"&signature={signature}";
        }

        return queryString;
    }

    public string GenerateSignature(string queryString)
    {
        using var hmac = new HMACSHA256(Encoding.UTF8.GetBytes(_options.ApiSecret));
        var hash = hmac.ComputeHash(Encoding.UTF8.GetBytes(queryString));
        return BitConverter.ToString(hash).Replace("-", "").ToLower();
    }
}
