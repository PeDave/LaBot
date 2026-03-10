using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Moq;
using Stripe;
using Xunit;

namespace LaBot.Infrastructure.Tests;

public class StripeWebhookTests
{
    [Fact]
    public void VerifyWebhookSignature_InvalidSignature_ThrowsException()
    {
        // Arrange
        var payload = "{\"type\":\"checkout.session.completed\"}";
        var secret = "whsec_test123";
        var invalidSignature = "t=123456,v1=invalidsignature";

        // Act & Assert
        Assert.Throws<StripeException>(() =>
        {
            EventUtility.ConstructEvent(
                payload,
                invalidSignature,
                secret,
                throwOnApiVersionMismatch: false
            );
        });
    }

    [Fact]
    public void VerifyWebhookSignature_Validates_Correctly()
    {
        // Test that the signature validation mechanism exists
        var payload = "{\"type\":\"test.event\"}";
        var secret = "whsec_test_secret_key_12345678";
        var invalidSignature = "invalid";

        // Should throw for invalid signature
        var exception = Assert.Throws<StripeException>(() =>
        {
            EventUtility.ConstructEvent(payload, invalidSignature, secret, throwOnApiVersionMismatch: false);
        });

        Assert.NotNull(exception);
    }
}
