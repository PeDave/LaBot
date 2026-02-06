namespace LaBot.Domain.Entities;

public class Tenant
{
    public Guid Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
    public bool IsActive { get; set; } = true;

    // Navigation properties
    public virtual ICollection<User> Users { get; set; } = new List<User>();
    public virtual ICollection<ExchangeApiKey> ExchangeApiKeys { get; set; } = new List<ExchangeApiKey>();
    public virtual ICollection<BotInstance> BotInstances { get; set; } = new List<BotInstance>();
}
