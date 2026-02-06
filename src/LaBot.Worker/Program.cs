using LaBot.Worker;

var builder = Host.CreateApplicationBuilder(args);
builder.Services.AddHostedService<BotEngine>();

var host = builder.Build();
host.Run();
