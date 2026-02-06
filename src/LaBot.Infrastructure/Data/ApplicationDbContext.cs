using LaBot.Domain.Entities;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;

namespace LaBot.Infrastructure.Data;

public class ApplicationDbContext : IdentityDbContext<ApplicationUser, IdentityRole<Guid>, Guid>
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
        : base(options)
    {
    }

    public DbSet<Tenant> Tenants => Set<Tenant>();
    public new DbSet<User> Users => Set<User>();
    public DbSet<ExchangeApiKey> ExchangeApiKeys => Set<ExchangeApiKey>();
    public DbSet<Candle> Candles => Set<Candle>();
    public DbSet<WalletSnapshot> WalletSnapshots => Set<WalletSnapshot>();
    public DbSet<BotInstance> BotInstances => Set<BotInstance>();
    public DbSet<BotState> BotStates => Set<BotState>();
    public DbSet<Signal> Signals => Set<Signal>();

    protected override void OnModelCreating(ModelBuilder builder)
    {
        base.OnModelCreating(builder);

        // Tenant configuration
        builder.Entity<Tenant>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Name).IsRequired().HasMaxLength(200);
            entity.HasIndex(e => e.Name);
        });

        // User configuration
        builder.Entity<User>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Email).IsRequired().HasMaxLength(256);
            entity.Property(e => e.UserName).IsRequired().HasMaxLength(256);
            entity.HasIndex(e => e.Email).IsUnique();
            entity.HasIndex(e => new { e.TenantId, e.UserName });

            entity.HasOne(e => e.Tenant)
                .WithMany(t => t.Users)
                .HasForeignKey(e => e.TenantId)
                .OnDelete(DeleteBehavior.Restrict);
        });

        // ExchangeApiKey configuration
        builder.Entity<ExchangeApiKey>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.ExchangeName).IsRequired().HasMaxLength(50);
            entity.Property(e => e.ApiKey).IsRequired().HasMaxLength(500);
            entity.Property(e => e.ApiSecret).IsRequired().HasMaxLength(500);
            entity.Property(e => e.Passphrase).HasMaxLength(100);
            entity.HasIndex(e => new { e.TenantId, e.ExchangeName });

            entity.HasOne(e => e.Tenant)
                .WithMany(t => t.ExchangeApiKeys)
                .HasForeignKey(e => e.TenantId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // Candle configuration
        builder.Entity<Candle>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Symbol).IsRequired().HasMaxLength(20);
            entity.Property(e => e.ExchangeName).IsRequired().HasMaxLength(50);
            entity.Property(e => e.Open).HasPrecision(18, 8);
            entity.Property(e => e.High).HasPrecision(18, 8);
            entity.Property(e => e.Low).HasPrecision(18, 8);
            entity.Property(e => e.Close).HasPrecision(18, 8);
            entity.Property(e => e.Volume).HasPrecision(18, 8);
            entity.HasIndex(e => new { e.Symbol, e.ExchangeName, e.Interval, e.OpenTime }).IsUnique();
        });

        // WalletSnapshot configuration
        builder.Entity<WalletSnapshot>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.ExchangeName).IsRequired().HasMaxLength(50);
            entity.Property(e => e.Asset).IsRequired().HasMaxLength(20);
            entity.Property(e => e.TotalBalance).HasPrecision(18, 8);
            entity.Property(e => e.AvailableBalance).HasPrecision(18, 8);
            entity.Property(e => e.LockedBalance).HasPrecision(18, 8);
            entity.HasIndex(e => new { e.TenantId, e.SnapshotTime });

            entity.HasOne(e => e.Tenant)
                .WithMany()
                .HasForeignKey(e => e.TenantId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // BotInstance configuration
        builder.Entity<BotInstance>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Name).IsRequired().HasMaxLength(200);
            entity.Property(e => e.StrategyName).IsRequired().HasMaxLength(100);
            entity.Property(e => e.ExchangeName).IsRequired().HasMaxLength(50);
            entity.Property(e => e.Symbol).IsRequired().HasMaxLength(20);
            entity.HasIndex(e => new { e.TenantId, e.Name });

            entity.HasOne(e => e.Tenant)
                .WithMany(t => t.BotInstances)
                .HasForeignKey(e => e.TenantId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // BotState configuration
        builder.Entity<BotState>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => new { e.BotInstanceId, e.Timestamp });

            entity.HasOne(e => e.BotInstance)
                .WithMany(b => b.BotStates)
                .HasForeignKey(e => e.BotInstanceId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // Signal configuration
        builder.Entity<Signal>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Symbol).IsRequired().HasMaxLength(20);
            entity.Property(e => e.Reason).HasMaxLength(500);
            entity.Property(e => e.Price).HasPrecision(18, 8);
            entity.Property(e => e.Quantity).HasPrecision(18, 8);
            entity.HasIndex(e => new { e.BotInstanceId, e.CreatedAt });

            entity.HasOne(e => e.BotInstance)
                .WithMany(b => b.Signals)
                .HasForeignKey(e => e.BotInstanceId)
                .OnDelete(DeleteBehavior.Cascade);
        });
    }
}
