using LaBot.Application.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace LaBot.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class AIController : ControllerBase
{
    private readonly IAIService _aiService;
    private readonly ILogger<AIController> _logger;

    public AIController(IAIService aiService, ILogger<AIController> logger)
    {
        _aiService = aiService;
        _logger = logger;
    }

    /// <summary>
    /// Generate a text completion from a prompt
    /// </summary>
    [HttpPost("completion")]
    public async Task<IActionResult> GenerateCompletion([FromBody] CompletionRequest request, CancellationToken cancellationToken)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(request.Prompt))
            {
                return BadRequest(new { error = "Prompt is required" });
            }

            var completion = await _aiService.GenerateCompletionAsync(request.Prompt, cancellationToken);
            return Ok(new { completion });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating completion");
            return StatusCode(500, new { error = "Failed to generate completion" });
        }
    }

    /// <summary>
    /// Analyze market data for a cryptocurrency
    /// </summary>
    [HttpPost("analyze-market")]
    public async Task<IActionResult> AnalyzeMarket([FromBody] MarketAnalysisRequest request, CancellationToken cancellationToken)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(request.Symbol))
            {
                return BadRequest(new { error = "Symbol is required" });
            }

            if (request.CurrentPrice <= 0)
            {
                return BadRequest(new { error = "Current price must be positive" });
            }

            var result = await _aiService.AnalyzeMarketAsync(request, cancellationToken);
            return Ok(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error analyzing market for {Symbol}", request.Symbol);
            return StatusCode(500, new { error = "Failed to analyze market" });
        }
    }

    /// <summary>
    /// Health check for AI service
    /// </summary>
    [HttpGet("health")]
    public IActionResult Health()
    {
        return Ok(new
        {
            status = "healthy",
            service = "AI",
            timestamp = DateTime.UtcNow
        });
    }
}

public record CompletionRequest(string Prompt);
