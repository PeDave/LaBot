using Stripe;

namespace LaBot.Application.Interfaces;

public interface IStripeService
{
    Task<string> CreateCheckoutSessionAsync(string userId, string priceId, CancellationToken cancellationToken = default);
    Task HandleWebhookAsync(string payload, string signature, CancellationToken cancellationToken = default);
    Task HandleCheckoutSessionCompletedAsync(Stripe.Checkout.Session session, CancellationToken cancellationToken = default);
    Task HandleSubscriptionCreatedAsync(Subscription subscription, CancellationToken cancellationToken = default);
    Task HandleSubscriptionUpdatedAsync(Subscription subscription, CancellationToken cancellationToken = default);
    Task HandleSubscriptionDeletedAsync(Subscription subscription, CancellationToken cancellationToken = default);
}
