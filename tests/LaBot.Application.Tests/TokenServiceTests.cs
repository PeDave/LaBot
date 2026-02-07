using LaBot.Application.Services;
using Microsoft.Extensions.Configuration;
using System.Security.Claims;
using Xunit;

namespace LaBot.Application.Tests;

public class TokenServiceTests
{
    [Fact]
    public void GenerateToken_ValidInput_ReturnsToken()
    {
        // Arrange
        var service = CreateTokenService();
        var userId = Guid.NewGuid().ToString();
        var email = "test@example.com";
        var roles = new[] { "Basic", "User" };

        // Act
        var token = service.GenerateToken(userId, email, roles);

        // Assert
        Assert.NotNull(token);
        Assert.NotEmpty(token);
        Assert.Contains(".", token); // JWT format check
    }

    [Fact]
    public void ValidateToken_ValidToken_ReturnsPrincipal()
    {
        // Arrange
        var service = CreateTokenService();
        var userId = Guid.NewGuid().ToString();
        var email = "test@example.com";
        var roles = new[] { "Basic" };
        
        var token = service.GenerateToken(userId, email, roles);

        // Act
        var principal = service.ValidateToken(token);

        // Assert
        Assert.NotNull(principal);
        var userIdClaim = principal.FindFirst(ClaimTypes.NameIdentifier);
        var emailClaim = principal.FindFirst(ClaimTypes.Email);
        var roleClaim = principal.FindFirst(ClaimTypes.Role);

        Assert.NotNull(userIdClaim);
        Assert.Equal(userId, userIdClaim.Value);
        Assert.NotNull(emailClaim);
        Assert.Equal(email, emailClaim.Value);
        Assert.NotNull(roleClaim);
        Assert.Equal("Basic", roleClaim.Value);
    }

    [Fact]
    public void ValidateToken_InvalidToken_ReturnsNull()
    {
        // Arrange
        var service = CreateTokenService();
        var invalidToken = "invalid.token.here";

        // Act
        var principal = service.ValidateToken(invalidToken);

        // Assert
        Assert.Null(principal);
    }

    [Fact]
    public void ValidateToken_ExpiredToken_ReturnsNull()
    {
        // Arrange - Create a token service with very short expiration
        var config = new Dictionary<string, string>
        {
            ["Jwt:SecretKey"] = "YourSuperSecretKeyThatIsAtLeast32CharactersLong!",
            ["Jwt:Issuer"] = "LaBot",
            ["Jwt:Audience"] = "LaBot",
            ["Jwt:ExpirationMinutes"] = "-1" // Already expired
        };
        var configuration = new ConfigurationBuilder()
            .AddInMemoryCollection(config!)
            .Build();
        
        var service = new TokenService(configuration);
        var userId = Guid.NewGuid().ToString();
        var email = "test@example.com";
        var roles = new[] { "Basic" };
        
        var token = service.GenerateToken(userId, email, roles);

        // Act
        var principal = service.ValidateToken(token);

        // Assert
        Assert.Null(principal); // Expired token should be invalid
    }

    [Fact]
    public void GenerateToken_MultipleRoles_IncludesAllRoles()
    {
        // Arrange
        var service = CreateTokenService();
        var userId = Guid.NewGuid().ToString();
        var email = "admin@example.com";
        var roles = new[] { "Admin", "Pro", "User" };

        // Act
        var token = service.GenerateToken(userId, email, roles);
        var principal = service.ValidateToken(token);

        // Assert
        Assert.NotNull(principal);
        var roleClaims = principal.FindAll(ClaimTypes.Role).ToList();
        Assert.Equal(3, roleClaims.Count);
        Assert.Contains(roleClaims, c => c.Value == "Admin");
        Assert.Contains(roleClaims, c => c.Value == "Pro");
        Assert.Contains(roleClaims, c => c.Value == "User");
    }

    private static ITokenService CreateTokenService()
    {
        var config = new Dictionary<string, string>
        {
            ["Jwt:SecretKey"] = "YourSuperSecretKeyThatIsAtLeast32CharactersLong!",
            ["Jwt:Issuer"] = "LaBot",
            ["Jwt:Audience"] = "LaBot",
            ["Jwt:ExpirationMinutes"] = "60"
        };

        var configuration = new ConfigurationBuilder()
            .AddInMemoryCollection(config!)
            .Build();

        return new TokenService(configuration);
    }
}
