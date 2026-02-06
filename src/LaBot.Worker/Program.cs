using LaBot.Exchanges.BingX.Adapters;
using LaBot.Exchanges.BingX.Configuration;
using LaBot.Exchanges.BingX.Http;
using LaBot.Worker;
using LaBot.Worker.Services;
using Microsoft.Extensions.Options;

var builder = Host.CreateApplicationBuilder(args);

// Configure BingX options from environment variables and configuration
builder.Services.Configure<BingXOptions>(options =>
{
    var config = builder.Configuration;
    options.ApiKey = Environment.GetEnvironmentVariable("BINGX_API_KEY") ?? config["BingX:ApiKey"] ?? string.Empty;
    options.ApiSecret = Environment.GetEnvironmentVariable("BINGX_API_SECRET") ?? config["BingX:ApiSecret"] ?? string.Empty;
    options.BaseUrl = Environment.GetEnvironmentVariable("BINGX_BASE_URL") ?? config["BingX:BaseUrl"] ?? "https://open-api.bingx.com";

    if (int.TryParse(Environment.GetEnvironmentVariable("BINGX_RECV_WINDOW"), out var recvWindow))
    {
        options.RecvWindow = recvWindow;
    }
    else
    {
        options.RecvWindow = config.GetValue<int>("BingX:RecvWindow", 5000);
    }

    if (int.TryParse(Environment.GetEnvironmentVariable("BINGX_POLL_INTERVAL_SECONDS"), out var pollInterval))
    {
        options.PollIntervalSeconds = pollInterval;
    }
    else
    {
        options.PollIntervalSeconds = config.GetValue<int>("BingX:PollIntervalSeconds", 10);
    }
});

// Register BingX services
builder.Services.AddHttpClient<BingXRestClient>();
builder.Services.AddSingleton(sp =>
{
    var options = sp.GetRequiredService<IOptions<BingXOptions>>().Value;
    var httpClientFactory = sp.GetRequiredService<IHttpClientFactory>();
    var httpClient = httpClientFactory.CreateClient(nameof(BingXRestClient));
    var logger = sp.GetRequiredService<ILogger<BingXRestClient>>();
    return new BingXRestClient(httpClient, options, logger);
});
builder.Services.AddSingleton<BingXAdapter>();

// Register background services
builder.Services.AddHostedService<BotEngine>();

// Only add BingXBalancePoller if API credentials are configured
var apiKey = Environment.GetEnvironmentVariable("BINGX_API_KEY") ?? builder.Configuration["BingX:ApiKey"];
if (!string.IsNullOrEmpty(apiKey))
{
    builder.Services.AddHostedService<BingXBalancePoller>();
}

var host = builder.Build();
host.Run();
