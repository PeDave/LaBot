using LaBot.Exchanges.BingX.Adapters;

namespace LaBot.Worker.Services;

public class BingXBalancePoller : BackgroundService
{
    private readonly ILogger<BingXBalancePoller> _logger;
    private readonly BingXAdapter _adapter;
    private readonly int _pollIntervalSeconds;

    public BingXBalancePoller(
        ILogger<BingXBalancePoller> logger,
        BingXAdapter adapter,
        IConfiguration configuration)
    {
        _logger = logger;
        _adapter = adapter;
        _pollIntervalSeconds = configuration.GetValue<int>("BingX:PollIntervalSeconds", 10);
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("BingX Balance Poller starting. Poll interval: {IntervalSeconds}s", _pollIntervalSeconds);

        // Fetch symbols once at startup
        await FetchSymbolsAsync(stoppingToken);

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await FetchBalancesAsync(stoppingToken);
                await Task.Delay(TimeSpan.FromSeconds(_pollIntervalSeconds), stoppingToken);
            }
            catch (TaskCanceledException)
            {
                _logger.LogInformation("BingX Balance Poller cancellation requested");
                break;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in BingX balance polling loop");
                await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken);
            }
        }

        _logger.LogInformation("BingX Balance Poller stopped");
    }

    private async Task FetchSymbolsAsync(CancellationToken cancellationToken)
    {
        try
        {
            var symbols = await _adapter.GetSymbolsAsync(cancellationToken);
            _logger.LogInformation("Successfully fetched {Count} symbols from BingX", symbols.Count);

            if (symbols.Count > 0)
            {
                var sampleSymbols = symbols.Take(5).Select(s => s.Name);
                _logger.LogDebug("Sample symbols: {Symbols}", string.Join(", ", sampleSymbols));
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to fetch symbols from BingX");
        }
    }

    private async Task FetchBalancesAsync(CancellationToken cancellationToken)
    {
        try
        {
            var balances = await _adapter.GetAllBalancesAsync(cancellationToken);
            _logger.LogInformation("Successfully fetched {Count} balances from BingX", balances.Count);

            if (balances.Count > 0)
            {
                var totalValue = balances.Sum(b => b.Total);
                var availableValue = balances.Sum(b => b.Available);
                var lockedValue = balances.Sum(b => b.Locked);

                _logger.LogInformation(
                    "Balance summary - Total: {Total}, Available: {Available}, Locked: {Locked}",
                    totalValue,
                    availableValue,
                    lockedValue
                );

                foreach (var balance in balances.Take(10))
                {
                    _logger.LogDebug(
                        "Asset: {Asset}, Total: {Total}, Available: {Available}, Locked: {Locked}",
                        balance.Asset,
                        balance.Total,
                        balance.Available,
                        balance.Locked
                    );
                }
            }
            else
            {
                _logger.LogInformation("No balances found in BingX account");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to fetch balances from BingX");
        }
    }
}
