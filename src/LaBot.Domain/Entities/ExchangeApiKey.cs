namespace LaBot.Domain.Entities;

public class ExchangeApiKey
{
    public Guid Id { get; set; }
    public Guid TenantId { get; set; }
    public string ExchangeName { get; set; } = string.Empty; // "Bitget" or "BingX"
    public string ApiKey { get; set; } = string.Empty;
    public string ApiSecret { get; set; } = string.Empty;
    public string? Passphrase { get; set; } // For exchanges that require it (Bitget)
    public bool IsTestnet { get; set; } = false;
    public DateTime CreatedAt { get; set; }
    public DateTime? LastUsedAt { get; set; }
    public bool IsActive { get; set; } = true;
    
    // Navigation properties
    public virtual Tenant Tenant { get; set; } = null!;
}
