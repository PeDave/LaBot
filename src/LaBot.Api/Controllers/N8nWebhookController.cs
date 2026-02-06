using Microsoft.AspNetCore.Mvc;

namespace LaBot.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class N8nWebhookController : ControllerBase
{
    private readonly ILogger<N8nWebhookController> _logger;

    public N8nWebhookController(ILogger<N8nWebhookController> logger)
    {
        _logger = logger;
    }

    [HttpPost("signal")]
    public IActionResult ReceiveSignal([FromBody] SignalWebhookDto signal)
    {
        _logger.LogInformation("Received signal from n8n: {@Signal}", signal);

        // TODO: Process signal and create bot action
        // This would integrate with the bot engine to execute trades

        return Ok(new { status = "received", signalId = signal.SignalId });
    }

    [HttpGet("export")]
    public IActionResult ExportData([FromQuery] string tenantId, [FromQuery] string dataType)
    {
        _logger.LogInformation("Export request for tenant {TenantId}, type {DataType}", tenantId, dataType);

        // TODO: Export data for n8n integration
        // This could export wallet snapshots, bot states, signals, etc.

        return Ok(new { data = new[] { new { sample = "data" } } });
    }
}

public record SignalWebhookDto(
    string SignalId,
    string Symbol,
    string Action,
    decimal? Price,
    decimal? Quantity
);
