# Image2Model SaaS Architecture

## System Overview

Image2Model is transitioning from a single-user prototype to a multi-tenant SaaS platform for design agencies. This document outlines the technical architecture for the production system.

## Architecture Diagram

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│                 │     │                  │     │                 │
│  Cloudflare     │────▶│   Nginx          │────▶│   FastAPI       │
│  Tunnel         │     │   (Static Files) │     │   Backend       │
│                 │     │                  │     │                 │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                           │
                                ┌──────────────────────────┼──────────────────────────┐
                                │                          │                          │
                        ┌───────▼────────┐       ┌─────────▼────────┐      ┌──────────▼────────┐
                        │                │       │                  │      │                   │
                        │   PostgreSQL   │       │     Redis        │      │   Celery Workers  │
                        │   Database     │       │   (Cache/Queue)  │      │   (Multiple)      │
                        │                │       │                  │      │                   │
                        └────────────────┘       └──────────────────┘      └──────────┬────────┘
                                                                                       │
                                                                            ┌──────────▼────────┐
                                                                            │                   │
                                                                            │    FAL.AI API     │
                                                                            │   (External)      │
                                                                            │                   │
                                                                            └───────────────────┘
```

## Multi-Tenancy Design

### Database Schema

```sql
-- Core tenant isolation
companies
    ├── id (UUID, PK)
    ├── name
    ├── domain (unique)
    ├── credit_balance
    └── settings (JSONB)

users
    ├── id (UUID, PK)
    ├── company_id (FK)
    ├── email (unique)
    └── role (admin/user)

-- All data tables include company_id for isolation
job_history
    ├── id (UUID, PK)
    ├── company_id (FK)
    ├── user_id (FK)
    └── ...

api_usage
    ├── id (UUID, PK)
    ├── company_id (FK)
    └── ...
```

### File Storage Structure

```
/app/uploads/
    ├── {company_id}/
    │   ├── {job_id}/
    │   │   ├── image1.png
    │   │   └── image2.jpg
    │   └── ...
    └── ...

/app/results/
    ├── {company_id}/
    │   ├── {job_id}/
    │   │   ├── model1.glb
    │   │   └── model2.glb
    │   └── ...
    └── ...
```

## Authentication Flow

### JWT-Based Authentication

```python
# Token Structure
{
    "sub": "user_id",
    "company_id": "company_id",
    "email": "user@company.com",
    "role": "admin",
    "exp": 1234567890
}
```

### Authentication Middleware

```python
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Decode JWT
    # Verify user exists
    # Check company is active
    # Return user object with company context
```

## Credit System Design

### Credit Calculation

```
Base FAL.AI Cost × Markup = Credit Cost

Low Quality (1000 faces):    $0.10 × 3.5 = 35 credits
Medium Quality (5000 faces): $0.15 × 3.5 = 52 credits
High Quality (10000 faces):  $0.20 × 3.5 = 70 credits

1 credit = $0.01 (for simplicity)
```

### Credit Flow

1. **Pre-check**: Before processing, verify sufficient credits
2. **Reserve**: Temporarily reserve credits during processing
3. **Deduct**: On successful completion, deduct credits
4. **Refund**: On failure, release reserved credits

### Database Transactions

```python
# Atomic credit operations
with db.begin():
    company.credit_balance -= credits_needed
    api_usage = ApiUsage(...)
    db.add(api_usage)
    db.commit()
```

## API Rate Limiting

### Per-User Limits
- Upload: 10 requests/minute
- Processing: 100 images/hour
- Downloads: 1000 requests/hour

### Implementation
```python
@limiter.limit("10/minute")
@router.post("/upload")
async def upload_files():
    pass
```

## Security Architecture

### Access Control Layers

1. **Cloudflare Tunnel**: First line of defense
2. **JWT Authentication**: Valid token required
3. **Company Isolation**: Users can only access their company's data
4. **Role-Based Access**: Admin vs regular user permissions
5. **File Access**: Signed URLs with expiration

### Security Headers

```python
# Nginx configuration
add_header X-Frame-Options "SAMEORIGIN";
add_header X-Content-Type-Options "nosniff";
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000";
```

## Billing Integration

### Stripe Architecture

```
User Action → Create Checkout → Stripe Payment → Webhook → Credit Update
                                                    ↓
                                              Database Update
                                                    ↓
                                              Email Confirmation
```

### Webhook Security

```python
# Verify Stripe signature
sig_header = request.headers.get('stripe-signature')
event = stripe.Webhook.construct_event(
    payload, sig_header, webhook_secret
)
```

## Monitoring & Observability

### Metrics Collection

1. **Application Metrics**
   - Request latency
   - Error rates
   - Credit usage
   - FAL.AI API calls

2. **Business Metrics**
   - Revenue per company
   - Credit consumption rate
   - User activity
   - Job success rate

3. **System Metrics**
   - CPU/Memory usage
   - Disk space
   - Database connections
   - Redis memory

### Logging Strategy

```python
# Structured logging
logger.info("credit_deduction", extra={
    "company_id": company_id,
    "user_id": user_id,
    "credits": credits,
    "remaining": company.credit_balance
})
```

## Deployment Architecture

### Production Stack

- **Server**: Linode VPS (Ubuntu 22.04)
- **Reverse Proxy**: Nginx
- **Process Manager**: Systemd
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Queue**: Celery with Redis broker
- **Monitoring**: Prometheus + Grafana

### Zero-Downtime Deployment

1. Build new Docker images
2. Run database migrations
3. Start new containers alongside old
4. Health check new containers
5. Switch Nginx upstream
6. Stop old containers

## Scaling Considerations

### Horizontal Scaling Points

1. **Celery Workers**: Add more workers for processing
2. **Read Replicas**: PostgreSQL read replicas for reporting
3. **CDN**: CloudFlare for static assets
4. **Redis Cluster**: For high-throughput caching

### Bottleneck Mitigation

- **FAL.AI Rate Limits**: Queue management and backoff
- **Database Connections**: Connection pooling
- **File Storage**: Consider S3 for scale
- **Credit Calculations**: Redis for fast lookups

## Disaster Recovery

### Backup Strategy

1. **Database**: Daily automated backups, 30-day retention
2. **Files**: Weekly backups of last 7 days of files
3. **Configuration**: Git repository for all configs
4. **Secrets**: Encrypted backup of .env files

### Recovery Procedures

- **RTO (Recovery Time Objective)**: 4 hours
- **RPO (Recovery Point Objective)**: 24 hours
- **Runbook**: Documented recovery steps

## Performance Optimization

### Caching Strategy

```python
# Redis caching for frequent queries
@cache("company:{company_id}", ttl=300)
async def get_company_credits(company_id: str):
    return company.credit_balance
```

### Database Optimization

- Indexes on foreign keys
- Partitioning for large tables
- Query optimization
- Connection pooling

## Migration Path

### Phase 1: Single Company (Week 1-2)
- Basic auth and user management
- Manual credit management
- File isolation

### Phase 2: Multi-Company (Week 3-4)
- Company management
- Automated billing
- Admin tools

### Phase 3: Scale (Week 5+)
- Performance optimization
- Advanced features
- Analytics dashboard

## API Design Principles

### RESTful Endpoints

```
POST   /api/v1/auth/login
GET    /api/v1/credits/balance
POST   /api/v1/upload/batch
GET    /api/v1/jobs/{job_id}/status
GET    /api/v1/download/{job_id}/files
```

### Response Format

```json
{
    "status": "success|error",
    "data": {},
    "message": "Human readable message",
    "errors": []
}
```

## Testing Strategy

### Test Pyramid

1. **Unit Tests**: Core business logic
2. **Integration Tests**: API endpoints
3. **E2E Tests**: Critical user flows
4. **Load Tests**: Performance validation

### Test Data Isolation

```python
# Separate test database
TEST_DATABASE_URL = "postgresql://test_user@localhost/image2model_test"

# Test data factories
def create_test_company():
    return Company(
        name="Test Company",
        domain="test.com",
        credit_balance=1000
    )
```

## Compliance & Legal

### Data Privacy

- User data encryption at rest
- Secure transmission (HTTPS only)
- Data retention policies
- Right to deletion (GDPR)

### Terms of Service Key Points

- Users retain IP rights to images
- Service availability SLA
- Limitation of liability
- Acceptable use policy

## Future Enhancements

### Planned Features

1. **API Access**: REST API for programmatic access
2. **Webhooks**: Real-time notifications
3. **Team Collaboration**: Shared projects
4. **White Labeling**: Custom branding
5. **Advanced Analytics**: Usage insights
6. **Batch API**: Bulk processing endpoint

### Technical Debt Tracking

- [ ] Migrate to async SQLAlchemy
- [ ] Implement Redis Sentinel
- [ ] Add GraphQL API
- [ ] Kubernetes deployment
- [ ] Multi-region support

---

**Document Version**: 1.0  
**Architecture Review Date**: Before Phase 4 deployment  
**Next Update**: After first customer onboarding