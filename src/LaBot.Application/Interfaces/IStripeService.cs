namespace LaBot.Application.Interfaces;

public interface IStripeService
{
    Task<string> CreateCheckoutSessionAsync(string userId, string priceId, CancellationToken cancellationToken = default);
    Task HandleWebhookAsync(string payload, string signature, CancellationToken cancellationToken = default);
}
