# LaBot - Crypto Trading Bot Platform

## 🚀 Quick Start

**New to LaBot?** Start here:
1. 📖 **[PROJECT_INDEX.md](PROJECT_INDEX.md)** - Single source of truth for architecture, navigation, and local development
2. ✅ **[CHECKLIST.md](CHECKLIST.md)** - Systematic development checklist to stay on track

## 📚 Documentation Index

### Core Documentation
- **[PROJECT_INDEX.md](PROJECT_INDEX.md)** - Complete project map: architecture, where to find what, local dev quickstart, configuration guide, and tenancy architecture
- **[CHECKLIST.md](CHECKLIST.md)** - Master checklist for development workflow: CI/build gates, conventions, tenancy, auth, MVP, security, and deployment checks

### Setup & Operations
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete Ubuntu 24.04 production deployment runbook
- **[VENDOR_SETUP.md](VENDOR_SETUP.md)** - How to vendor JKorf exchange SDKs
- **[N8N_SETUP.md](N8N_SETUP.md)** - n8n installation and LaBot integration without Docker

### Technical Reference
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical overview and implementation details

## Overview
LaBot is a multi-tenant cryptocurrency trading bot platform built with .NET 8, Blazor Server, and PostgreSQL.

## Architecture at a Glance
- **Domain**: Core business entities and value objects
- **Application**: Business logic and service interfaces
- **Infrastructure**: Data access, EF Core, external service implementations
- **Exchanges.Core**: Exchange adapter interfaces and models
- **Exchanges.Bitget**: Bitget exchange adapter
- **Exchanges.BingX**: BingX exchange adapter
- **Web**: Blazor Server dashboard
- **Api**: REST API for webhooks and n8n integration
- **Worker**: Background bot engine service

## Key Features
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
For local development setup, see **[PROJECT_INDEX.md](PROJECT_INDEX.md)** - Local Development Quickstart section.

For production deployment, see **[DEPLOYMENT.md](DEPLOYMENT.md)**.

For exchange SDK setup, see **[VENDOR_SETUP.md](VENDOR_SETUP.md)**.

For n8n integration, see **[N8N_SETUP.md](N8N_SETUP.md)**.
