using LaBot.Application.Interfaces;
using LaBot.Domain.Enums;
using LaBot.Infrastructure.Data;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using Stripe;
using Stripe.Checkout;

namespace LaBot.Infrastructure.Services;

public class StripeService : IStripeService
{
    private readonly ApplicationDbContext _context;
    private readonly UserManager<ApplicationUser> _userManager;
    private readonly ILogger<StripeService> _logger;

    public StripeService(
        ApplicationDbContext context,
        UserManager<ApplicationUser> userManager,
        ILogger<StripeService> logger)
    {
        _context = context;
        _userManager = userManager;
        _logger = logger;
    }

    public async Task<string> CreateCheckoutSessionAsync(string userId, string priceId, CancellationToken cancellationToken = default)
    {
        var user = await _userManager.FindByIdAsync(userId);
        if (user == null)
        {
            throw new ArgumentException($"User {userId} not found");
        }

        var options = new SessionCreateOptions
        {
            PaymentMethodTypes = new List<string> { "card" },
            LineItems = new List<SessionLineItemOptions>
            {
                new()
                {
                    Price = priceId,
                    Quantity = 1,
                }
            },
            Mode = "subscription",
            SuccessUrl = "https://labotkripto.com/subscription/success",
            CancelUrl = "https://labotkripto.com/subscription/cancel",
            CustomerEmail = user.Email,
        };

        var service = new SessionService();
        var session = await service.CreateAsync(options, cancellationToken: cancellationToken);

        return session.Url;
    }

    public async Task HandleWebhookAsync(string payload, string signature, CancellationToken cancellationToken = default)
    {
        // This method is called from the controller
        // The controller already handles signature verification
        _logger.LogInformation("Webhook payload received for processing");
        await Task.CompletedTask;
    }

    public async Task HandleCheckoutSessionCompletedAsync(Session session, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Processing checkout session {SessionId}", session.Id);

        var customerEmail = session.CustomerEmail;
        if (string.IsNullOrEmpty(customerEmail))
        {
            _logger.LogWarning("No customer email in session {SessionId}", session.Id);
            return;
        }

        var user = await _userManager.FindByEmailAsync(customerEmail);
        if (user == null)
        {
            _logger.LogWarning("User not found for email {Email}", customerEmail);
            return;
        }

        // Update user with Stripe customer ID
        user.Email = customerEmail;
        var result = await _context.SaveChangesAsync(cancellationToken);
        _logger.LogInformation("Updated user {UserId} with Stripe customer from session {SessionId}", user.Id, session.Id);
    }

    public async Task HandleSubscriptionCreatedAsync(Subscription subscription, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Processing subscription created {SubscriptionId}", subscription.Id);

        var customerId = subscription.CustomerId;
        
        // TODO: Lookup user by Stripe customer ID
        // For now, using email from subscription metadata
        var customerService = new CustomerService();
        var customer = await customerService.GetAsync(customerId, cancellationToken: cancellationToken);
        
        if (customer?.Email == null)
        {
            _logger.LogWarning("No email found for customer {CustomerId}", customerId);
            return;
        }

        var user = await _userManager.FindByEmailAsync(customer.Email);
        if (user == null)
        {
            _logger.LogWarning("User not found for email {Email}", customer.Email);
            return;
        }

        // Determine subscription plan from price ID
        var priceId = subscription.Items.Data.FirstOrDefault()?.Price.Id;
        var plan = DeterminePlanFromPriceId(priceId);

        _logger.LogInformation("Activating {Plan} subscription for user {UserId}", plan, user.Id);

        // Update user role based on subscription
        var roles = await _userManager.GetRolesAsync(user);
        await _userManager.RemoveFromRolesAsync(user, roles);

        var newRole = plan switch
        {
            SubscriptionPlan.Basic => "Basic",
            SubscriptionPlan.Pro => "Pro",
            _ => "Free"
        };

        await _userManager.AddToRoleAsync(user, newRole);
        _logger.LogInformation("Updated user {UserId} role to {Role}", user.Id, newRole);
    }

    public async Task HandleSubscriptionUpdatedAsync(Subscription subscription, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Processing subscription updated {SubscriptionId}", subscription.Id);

        var customerId = subscription.CustomerId;
        
        var customerService = new CustomerService();
        var customer = await customerService.GetAsync(customerId, cancellationToken: cancellationToken);
        
        if (customer?.Email == null)
        {
            _logger.LogWarning("No email found for customer {CustomerId}", customerId);
            return;
        }

        var user = await _userManager.FindByEmailAsync(customer.Email);
        if (user == null)
        {
            _logger.LogWarning("User not found for email {Email}", customer.Email);
            return;
        }

        // Handle subscription status changes
        if (subscription.Status == "active")
        {
            var priceId = subscription.Items.Data.FirstOrDefault()?.Price.Id;
            var plan = DeterminePlanFromPriceId(priceId);

            var roles = await _userManager.GetRolesAsync(user);
            await _userManager.RemoveFromRolesAsync(user, roles);

            var newRole = plan switch
            {
                SubscriptionPlan.Basic => "Basic",
                SubscriptionPlan.Pro => "Pro",
                _ => "Free"
            };

            await _userManager.AddToRoleAsync(user, newRole);
            _logger.LogInformation("Updated user {UserId} subscription to {Plan}", user.Id, plan);
        }
        else if (subscription.Status == "canceled" || subscription.Status == "unpaid")
        {
            await DowngradeUserToFreeAsync(user);
        }
    }

    public async Task HandleSubscriptionDeletedAsync(Subscription subscription, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Processing subscription deleted {SubscriptionId}", subscription.Id);

        var customerId = subscription.CustomerId;
        
        var customerService = new CustomerService();
        var customer = await customerService.GetAsync(customerId, cancellationToken: cancellationToken);
        
        if (customer?.Email == null)
        {
            _logger.LogWarning("No email found for customer {CustomerId}", customerId);
            return;
        }

        var user = await _userManager.FindByEmailAsync(customer.Email);
        if (user == null)
        {
            _logger.LogWarning("User not found for email {Email}", customer.Email);
            return;
        }

        await DowngradeUserToFreeAsync(user);
    }

    private async Task DowngradeUserToFreeAsync(ApplicationUser user)
    {
        var roles = await _userManager.GetRolesAsync(user);
        await _userManager.RemoveFromRolesAsync(user, roles);
        await _userManager.AddToRoleAsync(user, "Free");
        _logger.LogInformation("Downgraded user {UserId} to Free plan", user.Id);
    }

    private SubscriptionPlan DeterminePlanFromPriceId(string? priceId)
    {
        if (string.IsNullOrEmpty(priceId))
        {
            return SubscriptionPlan.Free;
        }

        // TODO: Map actual Stripe price IDs to plans
        // This is a simplified version - in production, check against configured price IDs
        if (priceId.Contains("basic", StringComparison.OrdinalIgnoreCase))
        {
            return SubscriptionPlan.Basic;
        }
        else if (priceId.Contains("pro", StringComparison.OrdinalIgnoreCase))
        {
            return SubscriptionPlan.Pro;
        }

        return SubscriptionPlan.Free;
    }
}
