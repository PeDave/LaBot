# LaBot - Crypto Trading Bot Platform

## Overview
LaBot is a multi-tenant cryptocurrency trading bot platform built with .NET 8, Blazor Server, and PostgreSQL.

## Architecture
- **Domain**: Core business entities and value objects
- **Application**: Business logic and service interfaces
- **Infrastructure**: Data access, EF Core, external service implementations
- **Exchanges.Core**: Exchange adapter interfaces and models
- **Exchanges.Bitget**: Bitget exchange adapter
- **Exchanges.BingX**: BingX exchange adapter
- **Web**: Blazor Server dashboard
- **Api**: REST API for webhooks and n8n integration
- **Worker**: Background bot engine service

## Features
- Multi-user, multi-tenant architecture (tenant = user initially)
- ASP.NET Core Identity authentication with cookie-based auth
- Role-based access control (Admin/Pro/Basic/Free)
- Stripe subscription integration (Basic/Pro plans)
- Exchange integrations (Bitget, BingX) via adapter pattern
- Market data: OHLCV candles (15m, 30m, 1h, 4h, 1d)
- Bot engine with Martingale strategy v1
- n8n integration via webhooks

## Symbol Format
Internal symbol format: `BTC/USDT`, `ETH/USDT`
Exchange adapters handle conversion to exchange-specific formats.

## Subscription Tiers
- **Free**: 24h delayed data, limited features
- **Basic**: 1-2 symbols, real-time data
- **Pro**: Admin-approved symbols, all features
- **Admin**: Full access to all features

## Tech Stack
- .NET 8
- Blazor Server
- PostgreSQL
- Entity Framework Core 8
- ASP.NET Core Identity
- Stripe.net
- Npgsql

## Getting Started
See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment instructions.
See [VENDOR_SETUP.md](VENDOR_SETUP.md) for vendoring JKorf SDKs.
See [N8N_SETUP.md](N8N_SETUP.md) for n8n installation.
