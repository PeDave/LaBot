using Microsoft.AspNetCore.Identity;

namespace LaBot.Infrastructure.Data;

public class ApplicationUser : IdentityUser<Guid>
{
    public Guid TenantId { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? LastLoginAt { get; set; }
}
