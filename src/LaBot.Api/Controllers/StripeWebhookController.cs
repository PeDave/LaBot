using Microsoft.AspNetCore.Mvc;
using Stripe;

namespace LaBot.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class StripeWebhookController : ControllerBase
{
    private readonly ILogger<StripeWebhookController> _logger;
    private readonly IConfiguration _configuration;

    public StripeWebhookController(ILogger<StripeWebhookController> logger, IConfiguration configuration)
    {
        _logger = logger;
        _configuration = configuration;
    }

    [HttpPost]
    public async Task<IActionResult> HandleWebhook()
    {
        var json = await new StreamReader(HttpContext.Request.Body).ReadToEndAsync();
        var webhookSecret = _configuration["Stripe:WebhookSecret"];

        try
        {
            var stripeEvent = EventUtility.ConstructEvent(
                json,
                Request.Headers["Stripe-Signature"],
                webhookSecret
            );

            _logger.LogInformation("Stripe webhook received: {EventType}", stripeEvent.Type);

            // Handle the event
            switch (stripeEvent.Type)
            {
                case "checkout.session.completed":
                    var session = stripeEvent.Data.Object as Stripe.Checkout.Session;
                    _logger.LogInformation("Checkout session completed: {SessionId}", session?.Id);
                    // TODO: Update user subscription in database
                    break;

                case "customer.subscription.created":
                    var subscription = stripeEvent.Data.Object as Subscription;
                    _logger.LogInformation("Subscription created: {SubscriptionId}", subscription?.Id);
                    // TODO: Activate subscription for user
                    break;

                case "customer.subscription.updated":
                    subscription = stripeEvent.Data.Object as Subscription;
                    _logger.LogInformation("Subscription updated: {SubscriptionId}", subscription?.Id);
                    // TODO: Update subscription status
                    break;

                case "customer.subscription.deleted":
                    subscription = stripeEvent.Data.Object as Subscription;
                    _logger.LogInformation("Subscription deleted: {SubscriptionId}", subscription?.Id);
                    // TODO: Downgrade user to Free plan
                    break;

                default:
                    _logger.LogWarning("Unhandled event type: {EventType}", stripeEvent.Type);
                    break;
            }

            return Ok();
        }
        catch (StripeException e)
        {
            _logger.LogError(e, "Stripe webhook error");
            return BadRequest();
        }
    }
}
