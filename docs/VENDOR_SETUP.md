# Vendoring JKorf Exchange SDKs

LaBot uses exchange SDKs from JKorf but vendors them as source code rather than using NuGet packages. This gives us full control over the implementation and allows for customization.

## Required SDKs

1. **Bitget.Net**: https://github.com/JKorf/Bitget.Net
2. **BingX.Net**: https://github.com/JKorf/BingX.Net
3. **CryptoClients.Net**: https://github.com/JKorf/CryptoClients.Net

## Vendoring Steps

### 1. Clone the Repositories

```bash
# Create a vendor directory
mkdir -p vendor
cd vendor

# Clone the SDKs
git clone https://github.com/JKorf/Bitget.Net.git
git clone https://github.com/JKorf/BingX.Net.git
git clone https://github.com/JKorf/CryptoClients.Net.git
```

### 2. Copy Source Files

For each SDK, copy the source files into the respective exchange project:

#### Bitget.Net
```bash
# Copy Bitget.Net source files to src/LaBot.Exchanges.Bitget/Vendor/
cp -r vendor/Bitget.Net/Bitget.Net/* src/LaBot.Exchanges.Bitget/Vendor/

# Update namespaces in copied files to match LaBot.Exchanges.Bitget
# This can be done with a script or manually
```

#### BingX.Net
```bash
# Copy BingX.Net source files to src/LaBot.Exchanges.BingX/Vendor/
cp -r vendor/BingX.Net/BingX.Net/* src/LaBot.Exchanges.BingX/Vendor/

# Update namespaces in copied files to match LaBot.Exchanges.BingX
```

#### CryptoClients.Net
```bash
# This is a shared library, can be copied to src/LaBot.Exchanges.Core/Vendor/
cp -r vendor/CryptoClients.Net/CryptoClients.Net/* src/LaBot.Exchanges.Core/Vendor/
```

### 3. Update Project References

After copying, update the `.csproj` files to include the vendored source files:

```xml
<ItemGroup>
  <Compile Include="Vendor/**/*.cs" />
</ItemGroup>
```

### 4. Resolve Dependencies

The JKorf SDKs have dependencies that need to be added to the projects:
- CryptoExchange.Net
- Newtonsoft.Json
- Microsoft.Extensions.Logging

Add these via NuGet:
```bash
dotnet add package CryptoExchange.Net
dotnet add package Newtonsoft.Json
dotnet add package Microsoft.Extensions.Logging
```

### 5. Implement Adapters

The adapter classes (`BitgetAdapter.cs`, `BingXAdapter.cs`) currently have stub implementations marked with `// TODO: Implement using vendored SDK`.

After vendoring, implement these methods using the vendored SDK classes:

```csharp
// Example for Bitget
public async Task<OrderResult> PlaceMarketOrderAsync(string symbol, OrderSide side, decimal quantity, CancellationToken cancellationToken = default)
{
    // Convert internal symbol format (BTC/USDT) to Bitget format (BTCUSDT)
    var bitgetSymbol = symbol.Replace("/", "");
    
    // Use vendored Bitget SDK
    var client = new BitgetRestClient(/* credentials */);
    var result = await client.SpotApi.Trading.PlaceOrderAsync(
        bitgetSymbol,
        side == OrderSide.Buy ? Bitget.Net.Enums.OrderSide.Buy : Bitget.Net.Enums.OrderSide.Sell,
        Bitget.Net.Enums.OrderType.Market,
        quantity,
        cancellationToken: cancellationToken
    );
    
    // Convert result to internal OrderResult format
    return new OrderResult(
        OrderId: result.Data.OrderId,
        Symbol: symbol,
        Side: side,
        Quantity: quantity,
        Price: null,
        Status: ConvertStatus(result.Data.Status),
        Timestamp: DateTime.UtcNow
    );
}
```

## Maintenance

When updating the SDKs:
1. Pull latest changes from upstream repositories
2. Copy updated files to vendor directories
3. Run tests to ensure compatibility
4. Update adapter implementations if SDK APIs changed

## Why Vendor?

1. **Full Control**: Modify SDK code if needed for LaBot-specific requirements
2. **Version Stability**: Not affected by NuGet package updates or deprecations
3. **Debugging**: Easier to debug issues in the SDK code
4. **Customization**: Can add LaBot-specific extensions or modifications
5. **Build Reliability**: No dependency on external package sources during build
