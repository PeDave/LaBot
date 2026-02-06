using LaBot.Domain.Enums;

namespace LaBot.Domain.Entities;

public class Signal
{
    public Guid Id { get; set; }
    public Guid BotInstanceId { get; set; }
    public string Symbol { get; set; } = string.Empty;
    public OrderSide Side { get; set; }
    public decimal Price { get; set; }
    public decimal Quantity { get; set; }
    public string Reason { get; set; } = string.Empty; // Why the signal was generated
    public bool IsExecuted { get; set; } = false;
    public DateTime? ExecutedAt { get; set; }
    public DateTime CreatedAt { get; set; }
    
    // Navigation properties
    public virtual BotInstance BotInstance { get; set; } = null!;
}
