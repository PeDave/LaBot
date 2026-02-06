namespace LaBot.Domain.Entities;

public class BotState
{
    public Guid Id { get; set; }
    public Guid BotInstanceId { get; set; }
    public string StateJson { get; set; } = "{}"; // Current bot state
    public DateTime Timestamp { get; set; }
    public DateTime CreatedAt { get; set; }
    
    // Navigation properties
    public virtual BotInstance BotInstance { get; set; } = null!;
}
