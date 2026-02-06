using LaBot.Domain.Entities;

namespace LaBot.Application.Interfaces;

public interface IBotService
{
    Task<BotInstance> GetBotByIdAsync(Guid botId, CancellationToken cancellationToken = default);
    Task<List<BotInstance>> GetBotsByTenantAsync(Guid tenantId, CancellationToken cancellationToken = default);
    Task<BotInstance> CreateBotAsync(Guid tenantId, string name, string strategyName, string exchangeName, string symbol, CancellationToken cancellationToken = default);
    Task StartBotAsync(Guid botId, CancellationToken cancellationToken = default);
    Task StopBotAsync(Guid botId, CancellationToken cancellationToken = default);
}
