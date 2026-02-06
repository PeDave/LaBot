using LaBot.Domain.Entities;

namespace LaBot.Application.Interfaces;

public interface ITenantService
{
    Task<Tenant> GetTenantByIdAsync(Guid tenantId, CancellationToken cancellationToken = default);
    Task<Tenant> CreateTenantAsync(string name, CancellationToken cancellationToken = default);
}
