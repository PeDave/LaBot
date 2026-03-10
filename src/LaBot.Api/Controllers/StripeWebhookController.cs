using LaBot.Application.Interfaces;
using Microsoft.AspNetCore.Mvc;
using Stripe;

namespace LaBot.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class StripeWebhookController : ControllerBase
{
    private readonly ILogger<StripeWebhookController> _logger;
    private readonly IConfiguration _configuration;
    private readonly IStripeService _stripeService;

    public StripeWebhookController(
        ILogger<StripeWebhookController> logger,
        IConfiguration configuration,
        IStripeService stripeService)
    {
        _logger = logger;
        _configuration = configuration;
        _stripeService = stripeService;
    }

    [HttpPost]
    public async Task<IActionResult> HandleWebhook()
    {
        var json = await new StreamReader(HttpContext.Request.Body).ReadToEndAsync();
        var webhookSecret = _configuration["Stripe:WebhookSecret"];

        if (string.IsNullOrEmpty(webhookSecret))
        {
            _logger.LogWarning("Stripe webhook secret not configured");
            return BadRequest("Webhook secret not configured");
        }

        try
        {
            var stripeSignature = Request.Headers["Stripe-Signature"].ToString();
            
            // Verify webhook signature
            var stripeEvent = EventUtility.ConstructEvent(
                json,
                stripeSignature,
                webhookSecret,
                throwOnApiVersionMismatch: false
            );

            _logger.LogInformation("Stripe webhook received and verified: {EventType}", stripeEvent.Type);

            // Handle the event
            switch (stripeEvent.Type)
            {
                case "checkout.session.completed":
                    var session = stripeEvent.Data.Object as Stripe.Checkout.Session;
                    if (session != null)
                    {
                        await _stripeService.HandleCheckoutSessionCompletedAsync(session);
                    }
                    break;

                case "customer.subscription.created":
                    var subscriptionCreated = stripeEvent.Data.Object as Subscription;
                    if (subscriptionCreated != null)
                    {
                        await _stripeService.HandleSubscriptionCreatedAsync(subscriptionCreated);
                    }
                    break;

                case "customer.subscription.updated":
                    var subscriptionUpdated = stripeEvent.Data.Object as Subscription;
                    if (subscriptionUpdated != null)
                    {
                        await _stripeService.HandleSubscriptionUpdatedAsync(subscriptionUpdated);
                    }
                    break;

                case "customer.subscription.deleted":
                    var subscriptionDeleted = stripeEvent.Data.Object as Subscription;
                    if (subscriptionDeleted != null)
                    {
                        await _stripeService.HandleSubscriptionDeletedAsync(subscriptionDeleted);
                    }
                    break;

                default:
                    _logger.LogWarning("Unhandled event type: {EventType}", stripeEvent.Type);
                    break;
            }

            return Ok();
        }
        catch (StripeException e)
        {
            _logger.LogError(e, "Stripe webhook signature verification failed");
            return BadRequest("Invalid signature");
        }
        catch (Exception e)
        {
            _logger.LogError(e, "Error processing Stripe webhook");
            return StatusCode(500, "Webhook processing failed");
        }
    }
}
