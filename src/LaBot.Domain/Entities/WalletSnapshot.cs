namespace LaBot.Domain.Entities;

public class WalletSnapshot
{
    public Guid Id { get; set; }
    public Guid TenantId { get; set; }
    public string ExchangeName { get; set; } = string.Empty;
    public string Asset { get; set; } = string.Empty; // USDT, BTC, etc.
    public decimal TotalBalance { get; set; }
    public decimal AvailableBalance { get; set; }
    public decimal LockedBalance { get; set; }
    public DateTime SnapshotTime { get; set; }
    public DateTime CreatedAt { get; set; }
    
    // Navigation properties
    public virtual Tenant Tenant { get; set; } = null!;
}
