using LaBot.Domain.Enums;

namespace LaBot.Domain.Entities;

public class BotInstance
{
    public Guid Id { get; set; }
    public Guid TenantId { get; set; }
    public string Name { get; set; } = string.Empty;
    public string StrategyName { get; set; } = string.Empty; // "Martingale"
    public string ExchangeName { get; set; } = string.Empty;
    public string Symbol { get; set; } = string.Empty; // BTC/USDT
    public TradingMode TradingMode { get; set; } = TradingMode.Spot;
    public bool IsActive { get; set; } = false;
    public string ConfigurationJson { get; set; } = "{}"; // Strategy-specific config
    public DateTime CreatedAt { get; set; }
    public DateTime? LastRunAt { get; set; }
    
    // Navigation properties
    public virtual Tenant Tenant { get; set; } = null!;
    public virtual ICollection<BotState> BotStates { get; set; } = new List<BotState>();
    public virtual ICollection<Signal> Signals { get; set; } = new List<Signal>();
}
