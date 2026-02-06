using LaBot.Domain.Entities;

namespace LaBot.Application.Interfaces;

public interface IWalletService
{
    Task<List<WalletSnapshot>> GetWalletSnapshotsAsync(Guid tenantId, CancellationToken cancellationToken = default);
    Task<WalletSnapshot> CreateSnapshotAsync(Guid tenantId, string exchangeName, CancellationToken cancellationToken = default);
}
