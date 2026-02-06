# LaBot Development Checklist

> **Master checklist** for systematic, quality-driven development. Check off items as you complete them to track progress and prevent getting lost.

Use this checklist when:
- Starting work on LaBot (new developer onboarding)
- Setting up a new development environment
- Preparing for a production deployment
- Conducting a security or quality audit
- Planning feature development

---

## 📋 How to Use This Checklist

1. **Copy sections** relevant to your current task into your issue/PR description
2. **Check off items** using `- [x]` as you complete them
3. **Skip irrelevant sections** - not all items apply to every task
4. **Add custom items** specific to your feature or bugfix
5. **Reference this checklist** in planning and code review

---

## 🔨 Phase 1: CI/Build Gates

### GitHub Actions Workflows
- [x] Create `.github/workflows/ci.yml` - Build, test, and format check on push/PR ✅
- [x] NuGet package caching configured for fast builds ✅
- [x] Code formatting verification with `dotnet format` ✅
- [ ] Add workflow status badges to root README.md
- [ ] Configure branch protection rules requiring checks to pass

**CI Workflow includes:**
- ✅ Runs on pull requests (all branches) and pushes to main
- ✅ .NET 8 SDK setup
- ✅ NuGet package caching
- ✅ `dotnet restore` for entire solution
- ✅ `dotnet build` in Release configuration with warnings as errors
- ✅ `dotnet test` with detailed output
- ✅ `dotnet format --verify-no-changes` for code formatting

### Build Verification
- [x] `dotnet restore` succeeds for entire solution ✅
- [x] `dotnet build` succeeds with zero warnings ✅
- [x] `dotnet build -c Release` succeeds ✅
- [x] All test projects compile successfully ✅
- [x] No package restore errors or version conflicts ✅

### Test Gate
- [x] `dotnet test` runs successfully ✅
- [x] All existing tests pass ✅
- [ ] Test coverage report generated (if using coverlet or similar)
- [ ] Critical paths have unit tests (authentication, tenancy, trading logic)
- [ ] Integration tests run against test database

---

## 📁 Phase 2: Repository Conventions

### Solution Structure
- [ ] Verify all projects are included in `LaBot.slnx`
- [ ] Confirm project organization follows Clean Architecture (Domain → Application → Infrastructure → Presentation)
- [ ] Ensure consistent naming conventions (LaBot.* namespace)
- [ ] Verify project references are correct (no circular dependencies)

### Code Standards
- [x] Nullable reference types enabled (in all .csproj files) ✅
- [x] TreatWarningsAsErrors enforced via CI workflow ✅
- [x] Code formatting enforced via CI (`dotnet format --verify-no-changes`) ✅
- [ ] Create `Directory.Build.props` for shared build settings (optional - using project-level settings)
- [ ] Create `.editorconfig` for consistent code style (optional - using .NET defaults)
- [ ] Configure analyzers (StyleCop, Roslynator, or similar)
- [ ] Document code style guidelines in CONTRIBUTING.md (if not exists)

### Git Practices
- [ ] `.gitignore` properly excludes bin/, obj/, .vs/, user-specific files
- [ ] No secrets or sensitive data committed to repository
- [ ] Verify `appsettings.Production.json` is in .gitignore
- [ ] Commit messages follow conventional commits (or document convention)

### Documentation Standards
- [ ] All new documentation follows markdown best practices
- [ ] Code comments exist for complex business logic
- [ ] Public APIs have XML documentation comments
- [ ] README files exist in subdirectories where helpful

---

## 🏢 Phase 3: Tenancy Baseline Verification

### Database Schema
- [ ] Verify `Tenant` table exists with proper columns (Id, Name, CreatedAt, etc.)
- [ ] Confirm tenant-specific tables have `TenantId` foreign key
- [ ] Check indexes on `TenantId` columns for query performance
- [ ] Verify EF Core migrations include tenancy changes

### Data Isolation
- [ ] EF Core query filters configured for tenant isolation (if not using manual filtering)
- [ ] Verify `ApplicationDbContext` applies tenant filtering correctly
- [ ] Test that users cannot access other tenants' data
- [ ] Verify tenant context is set correctly in all endpoints (Web, Api, Worker)

### Tenant Management
- [ ] User registration automatically creates tenant (tenant = user model)
- [ ] Verify tenant is associated with user in Identity
- [ ] Test tenant creation workflow end-to-end
- [ ] Document tenant expansion plan (future: multiple users per tenant)

### Testing
- [ ] Unit tests for tenant isolation logic
- [ ] Integration tests with multiple tenants
- [ ] Verify cross-tenant data access is prevented
- [ ] Test tenant deletion/deactivation flows (if implemented)

---

## 🔐 Phase 4: AuthN/AuthZ Baseline Verification

### ASP.NET Core Identity Setup
- [ ] Identity configured in `LaBot.Web/Program.cs`
- [ ] Identity tables created in database (AspNetUsers, AspNetRoles, etc.)
- [ ] Password requirements configured (strength, complexity)
- [ ] Cookie authentication configured correctly
- [ ] Login/Register/Logout pages exist and work

### User Registration & Login
- [ ] Test user registration flow end-to-end
- [ ] Verify email confirmation (if enabled) or document as future feature
- [ ] Test login with valid credentials
- [ ] Test login with invalid credentials (error messages)
- [ ] Test logout functionality

### Role-Based Authorization
- [ ] Roles defined: Admin, Pro, Basic, Free
- [ ] Role assignment implemented (manual or automated)
- [ ] `[Authorize(Roles = "...")]` attributes applied to protected pages/endpoints
- [ ] Test access control for each role level
- [ ] Verify unauthorized users are redirected to login

### Security Best Practices
- [ ] HTTPS enforced in production (configured in Nginx/Kestrel)
- [ ] Secure cookies (HttpOnly, Secure flags set)
- [ ] CSRF protection enabled for forms
- [ ] No credentials or secrets in client-side code
- [ ] Sensitive operations require re-authentication (if applicable)

### API Authentication
- [ ] API endpoints have appropriate `[Authorize]` attributes
- [ ] Webhook endpoints verify signatures (Stripe webhook secret)
- [ ] n8n webhook endpoints secured (basic auth or custom auth)
- [ ] Test API authentication with valid and invalid credentials

---

## 🚀 Phase 5: Vertical Slice MVP

> Define and implement one complete end-to-end scenario to validate the entire stack.

### Example MVP: "User Registers, Subscribes, and Views Market Data"

**Scenario Steps:**
- [ ] User registers a new account (Web)
- [ ] User logs in (Web)
- [ ] User navigates to dashboard (Web)
- [ ] User subscribes to Basic plan via Stripe (Web → Api)
- [ ] Stripe webhook processes subscription (Api)
- [ ] User role upgraded to Basic (Database)
- [ ] User views market data for BTC/USDT (Web → Infrastructure → Exchange)
- [ ] Market data displayed correctly (Web)

### Testing the MVP
- [ ] Manual end-to-end test completed successfully
- [ ] Integration test covers the MVP scenario
- [ ] All components involved (Web, Api, Infrastructure, Exchange) work together
- [ ] Database state reflects expected changes after MVP
- [ ] Logs show expected activity at each step

### Documentation
- [ ] MVP scenario documented for QA/testing
- [ ] Known limitations or future enhancements noted
- [ ] User guide or walkthrough created (if applicable)

---

## 🔒 Phase 6: Security Baseline

### Secrets Management
- [ ] No secrets in appsettings.json files (use environment variables)
- [ ] Secrets stored in environment variables or secret manager
- [ ] Database connection strings use environment variables in production
- [ ] Stripe API keys loaded from environment variables
- [ ] Exchange API keys encrypted in database (per-tenant)

### Dependency Security
- [ ] Run `dotnet list package --vulnerable` to check for vulnerabilities
- [ ] Update vulnerable packages to patched versions
- [ ] Document any unavoidable vulnerable dependencies
- [ ] Set up automated dependency scanning (Dependabot, Snyk, or similar)

### Input Validation
- [ ] User inputs validated and sanitized (registration, forms)
- [ ] SQL injection prevented (EF Core parameterized queries)
- [ ] XSS protection in Blazor (automatic encoding, verify custom JavaScript)
- [ ] API endpoints validate request payloads

### Authentication & Authorization
- [ ] Password hashing uses ASP.NET Core Identity defaults (PBKDF2 or bcrypt)
- [ ] Session timeout configured appropriately
- [ ] Sensitive operations require elevated permissions
- [ ] Rate limiting implemented on login/API endpoints (if applicable)

### Data Protection
- [ ] Tenant data isolation verified (cannot access other tenant data)
- [ ] Exchange API keys encrypted at rest (use Data Protection API or similar)
- [ ] Sensitive data not logged (no passwords, API keys in logs)
- [ ] HTTPS enforced for all external communication

### Webhooks Security
- [ ] Stripe webhook signature verification implemented
- [ ] n8n webhook endpoints use authentication (basic auth or custom)
- [ ] Webhook endpoints validate payload structure
- [ ] Webhook replay attacks prevented (if applicable)

---

## 🛠️ Phase 7: Operations & Deployment Sanity Checks

### Local Development
- [ ] `dotnet restore` and `dotnet build` work on fresh clone
- [ ] Database migrations run successfully
- [ ] All three services (Web, Api, Worker) start without errors
- [ ] Configuration instructions in documentation are accurate
- [ ] Developer can run tests without additional setup

### Production Readiness
- [ ] systemd service files exist for Web, Api, Worker (`ops/systemd/`)
- [ ] Nginx configuration exists and is valid (`ops/nginx/`)
- [ ] Environment variable templates provided (`ops/config/` or documentation)
- [ ] SSL/TLS configuration documented (Certbot/Let's Encrypt)
- [ ] Firewall rules documented (UFW or iptables)

### Database Operations
- [ ] EF Core migrations tested in staging environment
- [ ] Database backup strategy documented
- [ ] Rollback procedure documented (if migrations fail)
- [ ] Connection pooling configured appropriately
- [ ] Database indexes created for performance-critical queries

### Monitoring & Logging
- [ ] Application logs written to standard output (captured by systemd/journalctl)
- [ ] Log levels configured appropriately (Info for production, Debug for development)
- [ ] Critical errors logged with sufficient context
- [ ] Health check endpoints implemented (if applicable)
- [ ] Monitoring/alerting strategy documented (optional: Grafana, Prometheus, etc.)

### Deployment Procedure
- [ ] Deployment runbook tested end-to-end ([DEPLOYMENT.md](DEPLOYMENT.md))
- [ ] Zero-downtime deployment strategy (if required)
- [ ] Smoke tests defined for post-deployment validation
- [ ] Rollback procedure documented and tested

### Backup & Recovery
- [ ] Database backup procedure documented
- [ ] Database restore procedure tested
- [ ] Backup retention policy defined
- [ ] Configuration files backed up

---

## 🎯 Additional Feature-Specific Checklists

### Adding a New Exchange Adapter
- [ ] Create new project: `src/LaBot.Exchanges.YourExchange/`
- [ ] Implement `IExchangeAdapter` interface
- [ ] Implement `IExchangeWebSocketClient` interface (if applicable)
- [ ] Vendor exchange SDK following [VENDOR_SETUP.md](VENDOR_SETUP.md)
- [ ] Add unit tests for adapter
- [ ] Add integration tests with test API keys
- [ ] Register adapter in dependency injection
- [ ] Update documentation (PROJECT_INDEX.md, README.md)

### Adding a New Trading Strategy
- [ ] Define strategy interface in `LaBot.Application/`
- [ ] Implement strategy in `LaBot.Worker/`
- [ ] Add configuration for strategy parameters
- [ ] Add unit tests for strategy logic
- [ ] Add integration tests with mock exchange
- [ ] Document strategy behavior and parameters
- [ ] Register strategy in Worker service collection

### Adding a New Subscription Tier
- [ ] Define tier in Stripe dashboard
- [ ] Add tier to Stripe configuration
- [ ] Update `StripeWebhookController` to handle new tier
- [ ] Add role/permissions for new tier
- [ ] Update authorization policies
- [ ] Test subscription flow for new tier
- [ ] Update user-facing documentation

---

## ✅ Final Pre-Deployment Checklist

Run through this before any production deployment:

- [ ] All tests pass (`dotnet test`)
- [ ] No security vulnerabilities in dependencies
- [ ] Secrets configured in production environment
- [ ] Database migrations applied to production
- [ ] Smoke tests pass in staging environment
- [ ] Deployment runbook reviewed
- [ ] Rollback procedure reviewed
- [ ] Monitoring/alerting configured
- [ ] Stakeholders notified of deployment window
- [ ] Post-deployment smoke tests defined

---

## 📚 Reference Documentation

When working through this checklist, refer to:
- [PROJECT_INDEX.md](PROJECT_INDEX.md) - Architecture and navigation guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment runbook
- [VENDOR_SETUP.md](VENDOR_SETUP.md) - Exchange SDK setup
- [N8N_SETUP.md](N8N_SETUP.md) - n8n integration setup
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Technical overview

---

**Last Updated**: 2026-02-06

**Note**: This is a living document. Update it as the project evolves and new patterns emerge.
