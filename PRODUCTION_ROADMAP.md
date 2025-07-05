# 🚀 Image2Model SaaS Production Roadmap

## Overview
This document tracks the transformation of Image2Model from a working prototype to a production-ready SaaS platform for design agencies.

**Target Launch Date**: 6-7 weeks from start  
**Initial Customer**: Design agency (via girlfriend)  
**Revenue Model**: $10/user/month + credit-based usage  
**Deployment**: Private Linode with Cloudflare Tunnel

---

## 📊 Current State Analysis

### ✅ What We Have
- Core 3D model generation working (FAL.AI integration)
- Batch processing with parallel workers
- Real-time progress tracking (SSE)
- File upload/download system
- Error handling and retry logic
- Docker infrastructure
- Monitoring and health checks

### ❌ What We Need
- User authentication system
- Company/tenant management
- Credit-based billing system
- Usage tracking and analytics
- File isolation per company
- Admin dashboard
- Production security hardening

---

## 🎯 Phase 1: Foundation - Multi-User System (Week 1-2)

### 1.1 Database Schema Updates ⬜

**Location**: `backend/docker/postgres/init.sql`

```sql
-- Companies table for multi-tenancy
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) UNIQUE NOT NULL,
    credit_balance INTEGER DEFAULT 0,
    price_per_credit DECIMAL(10,4) DEFAULT 0.50,
    stripe_customer_id VARCHAR(255),
    subscription_status VARCHAR(50) DEFAULT 'trial',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Users within companies
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    company_id UUID REFERENCES companies(id),
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Track API usage for billing
CREATE TABLE api_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    company_id UUID REFERENCES companies(id),
    job_id VARCHAR(255),
    image_count INTEGER,
    credits_used INTEGER,
    fal_cost DECIMAL(10,4),
    quality_setting VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Job history for user dashboard
CREATE TABLE job_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id),
    company_id UUID REFERENCES companies(id),
    batch_id VARCHAR(255),
    file_count INTEGER,
    status VARCHAR(50),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_users_company ON users(company_id);
CREATE INDEX idx_api_usage_company ON api_usage(company_id, created_at);
CREATE INDEX idx_job_history_user ON job_history(user_id, created_at);
```

### 1.2 SQLAlchemy Models ⬜

**Create**: `backend/app/models/company.py`
```python
from sqlalchemy import Column, String, Integer, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base
import uuid

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, nullable=False)
    credit_balance = Column(Integer, default=0)
    price_per_credit = Column(Numeric(10, 4), default=0.50)
    stripe_customer_id = Column(String(255))
    subscription_status = Column(String(50), default='trial')
    created_at = Column(DateTime, server_default='NOW()')
    updated_at = Column(DateTime, server_default='NOW()')
```

**Create**: `backend/app/models/user.py`
```python
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255))
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'))
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, server_default='NOW()')
    
    # Relationships
    company = relationship("Company", back_populates="users")
```

### 1.3 Authentication System ⬜

**Create**: `backend/app/core/auth.py`
```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        return None
```

**Create**: `backend/app/api/endpoints/auth.py`
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.base import get_db
from app.models.user import User
from app.models.company import Company
from app.core.auth import verify_password, create_access_token, get_password_hash

router = APIRouter()

@router.post("/login")
async def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register")
async def register(email: str, password: str, company_name: str, db: Session = Depends(get_db)):
    # Extract domain from email
    domain = email.split('@')[1]
    
    # Check if company exists
    company = db.query(Company).filter(Company.domain == domain).first()
    if not company:
        # Create new company
        company = Company(name=company_name, domain=domain, credit_balance=100)  # 100 free credits
        db.add(company)
        db.commit()
    
    # Create user
    user = User(
        email=email,
        password_hash=get_password_hash(password),
        company_id=company.id,
        is_admin=True if not company.users else False  # First user is admin
    )
    db.add(user)
    db.commit()
    
    return {"message": "Registration successful", "company": company.name}
```

### 1.4 Frontend Authentication ⬜

**Create**: `frontend-simple/login.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Login - Image2Model</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="login-container">
        <h1>Image2Model</h1>
        <form id="loginForm">
            <input type="email" id="email" placeholder="Email" required>
            <input type="password" id="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <p>New user? <a href="#" id="showRegister">Register</a></p>
    </div>
    <script src="js/auth.js"></script>
</body>
</html>
```

**Create**: `frontend-simple/js/auth.js`
```javascript
class AuthManager {
    constructor() {
        this.token = localStorage.getItem('access_token');
        this.checkAuth();
    }
    
    async login(email, password) {
        const response = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, password})
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access_token);
            window.location.href = '/index.html';
        } else {
            throw new Error('Login failed');
        }
    }
    
    checkAuth() {
        if (!this.token && !window.location.pathname.includes('login')) {
            window.location.href = '/login.html';
        }
    }
    
    getAuthHeaders() {
        return {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
        };
    }
}

const auth = new AuthManager();
```

### 1.5 Update Existing Endpoints ⬜

**Update all endpoints to include user context**:
```python
# In backend/app/core/deps.py
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user

# Update upload.py
@router.post("/upload/batch")
async def upload_batch(
    files: List[UploadFile],
    user: User = Depends(get_current_user)
):
    # Add user_id and company_id to job creation
    job_id = str(uuid.uuid4())
    batch_dir = os.path.join(settings.UPLOAD_DIR, str(user.company_id), job_id)
```

---

## 🎯 Phase 2: Usage Tracking & Credits (Week 2-3)

### 2.1 Credit System Implementation ⬜

**Create**: `backend/app/core/pricing.py`
```python
from decimal import Decimal
from app.models.company import Company
from app.models.api_usage import ApiUsage
from sqlalchemy.orm import Session

# FAL.AI costs per image (approximate)
FAL_COSTS = {
    "low": Decimal("0.10"),    # 1000 faces
    "medium": Decimal("0.15"),  # 5000 faces
    "high": Decimal("0.20")     # 10000 faces
}

# Our pricing (3.5x markup)
CREDIT_COSTS = {
    "low": 35,     # 35 credits
    "medium": 52,   # 52 credits  
    "high": 70      # 70 credits
}

def calculate_credits_needed(quality: str, image_count: int) -> int:
    """Calculate credits needed for a job"""
    return CREDIT_COSTS.get(quality, 52) * image_count

def check_sufficient_credits(company: Company, credits_needed: int) -> bool:
    """Check if company has enough credits"""
    return company.credit_balance >= credits_needed

def deduct_credits(db: Session, company: Company, credits: int) -> bool:
    """Deduct credits from company balance"""
    if company.credit_balance >= credits:
        company.credit_balance -= credits
        db.commit()
        return True
    return False

def log_usage(db: Session, user_id: str, company_id: str, job_id: str, 
              image_count: int, credits_used: int, fal_cost: Decimal):
    """Log API usage for billing"""
    usage = ApiUsage(
        user_id=user_id,
        company_id=company_id,
        job_id=job_id,
        image_count=image_count,
        credits_used=credits_used,
        fal_cost=fal_cost
    )
    db.add(usage)
    db.commit()
```

**Update**: `backend/app/workers/tasks.py`
```python
# Add to process_file_in_batch function
from app.core.pricing import deduct_credits, log_usage

# Before processing
credits_needed = calculate_credits_needed(quality, 1)
if not check_sufficient_credits(company, credits_needed):
    raise Exception("Insufficient credits")

# After successful FAL.AI processing
deduct_credits(db, company, credits_needed)
log_usage(db, user_id, company_id, job_id, 1, credits_needed, fal_cost)
```

### 2.2 Usage Dashboard ⬜

**Create**: `frontend-simple/dashboard.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Dashboard - Image2Model</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <header>
        <nav>
            <a href="index.html">Home</a>
            <a href="dashboard.html" class="active">Dashboard</a>
            <a href="history.html">History</a>
            <span id="creditBalance" class="credit-display">Credits: Loading...</span>
        </nav>
    </header>
    
    <main class="dashboard">
        <h1>Usage Dashboard</h1>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Credits Remaining</h3>
                <p class="stat-value" id="creditsValue">-</p>
            </div>
            <div class="stat-card">
                <h3>Jobs This Month</h3>
                <p class="stat-value" id="jobsCount">-</p>
            </div>
            <div class="stat-card">
                <h3>Images Processed</h3>
                <p class="stat-value" id="imagesCount">-</p>
            </div>
        </div>
        
        <div class="usage-chart">
            <h2>Usage Over Time</h2>
            <canvas id="usageChart"></canvas>
        </div>
        
        <div class="recent-jobs">
            <h2>Recent Jobs</h2>
            <table id="recentJobsTable">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Images</th>
                        <th>Credits Used</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
    </main>
    
    <script src="js/dashboard.js"></script>
</body>
</html>
```

**Create**: `backend/app/api/endpoints/credits.py`
```python
@router.get("/credits/balance")
async def get_credit_balance(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == user.company_id).first()
    return {
        "balance": company.credit_balance,
        "price_per_credit": float(company.price_per_credit)
    }

@router.get("/credits/usage")
async def get_usage_history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = 30
):
    since = datetime.now() - timedelta(days=days)
    usage = db.query(ApiUsage).filter(
        ApiUsage.company_id == user.company_id,
        ApiUsage.created_at >= since
    ).all()
    
    return {
        "usage": [
            {
                "date": u.created_at,
                "credits": u.credits_used,
                "images": u.image_count,
                "user": u.user_id
            } for u in usage
        ],
        "total_credits": sum(u.credits_used for u in usage),
        "total_images": sum(u.image_count for u in usage)
    }
```

### 2.3 Low Credit Warnings ⬜

**Add to**: `backend/app/core/email.py`
```python
async def send_low_credit_warning(company: Company, balance: int):
    # Send email when credits < 20
    subject = "Low Credit Balance Warning"
    body = f"""
    Your Image2Model credit balance is low.
    
    Current balance: {balance} credits
    
    Please top up your credits to continue using the service.
    """
    
    # Send to all admin users in company
    for user in company.users:
        if user.is_admin:
            await send_email(user.email, subject, body)
```

---

## 🎯 Phase 3: Company Management (Week 3-4)

### 3.1 Company Admin Features ⬜

**Create**: `backend/app/api/endpoints/company.py`
```python
@router.get("/company/info")
async def get_company_info(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user.is_admin:
        raise HTTPException(403, "Admin access required")
    
    company = db.query(Company).filter(Company.id == user.company_id).first()
    users = db.query(User).filter(User.company_id == company.id).all()
    
    return {
        "company": {
            "name": company.name,
            "domain": company.domain,
            "credit_balance": company.credit_balance,
            "user_count": len(users),
            "created_at": company.created_at
        },
        "users": [
            {
                "email": u.email,
                "is_admin": u.is_admin,
                "last_login": u.last_login,
                "created_at": u.created_at
            } for u in users
        ]
    }

@router.post("/company/invite")
async def invite_user(
    email: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not user.is_admin:
        raise HTTPException(403, "Admin access required")
    
    # Verify email domain matches company
    domain = email.split('@')[1]
    company = db.query(Company).filter(Company.id == user.company_id).first()
    
    if domain != company.domain:
        raise HTTPException(400, f"Email must be from {company.domain}")
    
    # Send invitation email
    await send_invitation_email(email, company.name)
    
    return {"message": f"Invitation sent to {email}"}
```

### 3.2 File Isolation ⬜

**Update file paths throughout the codebase**:
```python
# In upload.py
def get_upload_path(company_id: str, job_id: str, filename: str) -> str:
    """Generate isolated file path per company"""
    return os.path.join(
        settings.UPLOAD_DIR,
        str(company_id),
        str(job_id),
        filename
    )

# In download.py - verify user has access
@router.get("/download/{job_id}/{filename}")
async def download_file(
    job_id: str,
    filename: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify job belongs to user's company
    job = db.query(JobHistory).filter(
        JobHistory.job_id == job_id,
        JobHistory.company_id == user.company_id
    ).first()
    
    if not job:
        raise HTTPException(404, "Job not found")
    
    file_path = get_result_path(user.company_id, job_id, filename)
    return FileResponse(file_path)
```

### 3.3 Company Admin UI ⬜

**Create**: `frontend-simple/company-admin.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Company Admin - Image2Model</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <header>
        <nav>
            <a href="index.html">Home</a>
            <a href="dashboard.html">Dashboard</a>
            <a href="company-admin.html" class="active">Admin</a>
        </nav>
    </header>
    
    <main class="admin-panel">
        <h1>Company Administration</h1>
        
        <section class="company-info">
            <h2>Company Details</h2>
            <div id="companyDetails"></div>
        </section>
        
        <section class="user-management">
            <h2>User Management</h2>
            <button onclick="showInviteModal()">Invite User</button>
            <table id="userTable">
                <thead>
                    <tr>
                        <th>Email</th>
                        <th>Role</th>
                        <th>Last Login</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </section>
        
        <section class="usage-summary">
            <h2>Company Usage Summary</h2>
            <div id="usageSummary"></div>
            <button onclick="downloadReport()">Download Report</button>
        </section>
    </main>
    
    <script src="js/company-admin.js"></script>
</body>
</html>
```

---

## 🎯 Phase 4: Production Deployment (Week 4-5)

### 4.1 Security Hardening ⬜

**Create**: `.env.production`
```bash
# Production Environment Variables
SECRET_KEY=<generate-strong-secret>
DATABASE_URL=postgresql://prod_user:strong_password@localhost:5432/image2model_prod
REDIS_URL=redis://localhost:6379/0

# Email Configuration
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<sendgrid-api-key>
FROM_EMAIL=noreply@image2model.com

# FAL.AI Production
FAL_API_KEY=<production-fal-key>

# Monitoring
SENTRY_DSN=<sentry-dsn>
```

**Update**: `backend/app/core/security.py`
```python
from itsdangerous import URLSafeTimedSerializer
from app.core.config import settings

def generate_secure_token(data: dict) -> str:
    """Generate time-limited secure token for file downloads"""
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(data)

def verify_secure_token(token: str, max_age: int = 3600) -> dict:
    """Verify and decode secure token"""
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        return serializer.loads(token, max_age=max_age)
    except:
        return None

# In download.py - secure file URLs
@router.get("/download/secure/{token}")
async def download_secure(token: str):
    data = verify_secure_token(token)
    if not data:
        raise HTTPException(403, "Invalid or expired token")
    
    file_path = data.get("path")
    return FileResponse(file_path)
```

### 4.2 Rate Limiting ⬜

**Install**: `pip install slowapi`

**Create**: `backend/app/core/rate_limit.py`
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Create limiter
limiter = Limiter(key_func=get_remote_address)

# Apply to routes
# In main.py
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# In upload.py
@router.post("/upload/batch")
@limiter.limit("10/minute")  # 10 uploads per minute
async def upload_batch(...):
    pass
```

### 4.3 Cloudflare Tunnel Setup ⬜

**On Linode server**:
```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Login to Cloudflare
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create image2model

# Create config file
sudo nano /etc/cloudflared/config.yml
```

**Config**: `/etc/cloudflared/config.yml`
```yaml
tunnel: <tunnel-id>
credentials-file: /home/cloudflared/.cloudflared/<tunnel-id>.json

ingress:
  # Main application
  - hostname: app.image2model.com
    service: http://localhost:8000
    originRequest:
      noTLSVerify: true
  
  # Static files
  - hostname: app.image2model.com
    path: /static/*
    service: http://localhost:3000
  
  # Catch-all
  - service: http_status:404
```

**Start tunnel**:
```bash
# Run as service
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

### 4.4 Backup Strategy ⬜

**Create**: `/home/scripts/backup.sh`
```bash
#!/bin/bash
# Daily backup script

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
docker exec image2model-postgres pg_dump -U postgres image2model | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup uploaded files (last 7 days only)
find /app/uploads -type f -mtime -7 | tar czf $BACKUP_DIR/uploads_$DATE.tar.gz -T -

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -type f -mtime +30 -delete

# Upload to S3 (optional)
# aws s3 sync $BACKUP_DIR s3://image2model-backups/
```

**Crontab**:
```bash
# Add to crontab
0 2 * * * /home/scripts/backup.sh >> /var/log/backup.log 2>&1
```

---

## 🎯 Phase 5: Billing Integration (Week 5-6)

### 5.1 Stripe Setup ⬜

**Install**: `pip install stripe`

**Create**: `backend/app/api/endpoints/billing.py`
```python
import stripe
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

@router.post("/billing/create-checkout")
async def create_checkout_session(
    credits: int = 100,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Stripe checkout session for credit purchase"""
    company = db.query(Company).filter(Company.id == user.company_id).first()
    
    # Create or get Stripe customer
    if not company.stripe_customer_id:
        customer = stripe.Customer.create(
            email=user.email,
            metadata={"company_id": str(company.id)}
        )
        company.stripe_customer_id = customer.id
        db.commit()
    
    # Create checkout session
    session = stripe.checkout.Session.create(
        customer=company.stripe_customer_id,
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': f'{credits} Credits',
                    'description': 'Image2Model processing credits'
                },
                'unit_amount': int(credits * company.price_per_credit * 100),  # in cents
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=settings.FRONTEND_URL + '/dashboard.html?payment=success',
        cancel_url=settings.FRONTEND_URL + '/dashboard.html?payment=cancelled',
        metadata={
            'company_id': str(company.id),
            'credits': credits
        }
    )
    
    return {"checkout_url": session.url}

@router.post("/billing/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhooks"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(400, "Invalid payload")
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Add credits to company
        company_id = session['metadata']['company_id']
        credits = int(session['metadata']['credits'])
        
        company = db.query(Company).filter(Company.id == company_id).first()
        company.credit_balance += credits
        db.commit()
        
        # Send confirmation email
        await send_purchase_confirmation(company, credits)
    
    return {"status": "success"}
```

### 5.2 Subscription Plans ⬜

**Database migration**:
```sql
CREATE TABLE subscription_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100),
    price_monthly DECIMAL(10,2),
    included_credits INTEGER,
    price_per_additional_credit DECIMAL(10,4),
    stripe_price_id VARCHAR(255)
);

-- Insert default plans
INSERT INTO subscription_plans (name, price_monthly, included_credits, price_per_additional_credit, stripe_price_id) VALUES
('Starter', 10.00, 100, 0.50, 'price_starter'),
('Professional', 25.00, 300, 0.40, 'price_professional'),
('Enterprise', 100.00, 1500, 0.30, 'price_enterprise');
```

---

## 🎯 Phase 6: Admin Tools (Week 6)

### 6.1 Super Admin Dashboard ⬜

**Create**: `backend/app/api/endpoints/admin.py` (enhanced)
```python
@router.get("/admin/metrics")
async def get_system_metrics(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify super admin (hardcode initially)
    if user.email not in settings.SUPER_ADMINS:
        raise HTTPException(403, "Super admin access required")
    
    # Get metrics
    total_companies = db.query(Company).count()
    total_users = db.query(User).count()
    total_jobs = db.query(JobHistory).count()
    
    # Revenue calculation
    revenue_this_month = db.query(
        func.sum(ApiUsage.credits_used * Company.price_per_credit)
    ).join(Company).filter(
        ApiUsage.created_at >= datetime.now().replace(day=1)
    ).scalar() or 0
    
    # FAL.AI costs
    fal_costs = db.query(func.sum(ApiUsage.fal_cost)).filter(
        ApiUsage.created_at >= datetime.now().replace(day=1)
    ).scalar() or 0
    
    return {
        "companies": total_companies,
        "users": total_users,
        "jobs": total_jobs,
        "revenue_month": float(revenue_this_month),
        "costs_month": float(fal_costs),
        "profit_month": float(revenue_this_month - fal_costs),
        "margin": f"{((revenue_this_month - fal_costs) / revenue_this_month * 100):.1f}%"
    }

@router.post("/admin/credits/adjust")
async def adjust_credits(
    company_id: str,
    credits: int,
    reason: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user.email not in settings.SUPER_ADMINS:
        raise HTTPException(403)
    
    company = db.query(Company).filter(Company.id == company_id).first()
    company.credit_balance += credits
    
    # Log adjustment
    db.add(CreditAdjustment(
        company_id=company_id,
        admin_id=user.id,
        credits=credits,
        reason=reason
    ))
    db.commit()
    
    return {"new_balance": company.credit_balance}
```

**Create**: `frontend-simple/admin/system-dashboard.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>System Admin - Image2Model</title>
    <link rel="stylesheet" href="../css/style.css">
    <style>
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #2563eb;
        }
        .profit { color: #10b981; }
        .cost { color: #ef4444; }
    </style>
</head>
<body>
    <header>
        <h1>System Administration</h1>
    </header>
    
    <main>
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>Total Companies</h3>
                <p class="metric-value" id="totalCompanies">-</p>
            </div>
            <div class="metric-card">
                <h3>Total Users</h3>
                <p class="metric-value" id="totalUsers">-</p>
            </div>
            <div class="metric-card">
                <h3>Revenue (Month)</h3>
                <p class="metric-value profit" id="revenue">-</p>
            </div>
            <div class="metric-card">
                <h3>FAL.AI Costs</h3>
                <p class="metric-value cost" id="costs">-</p>
            </div>
            <div class="metric-card">
                <h3>Profit Margin</h3>
                <p class="metric-value" id="margin">-</p>
            </div>
        </div>
        
        <section class="admin-actions">
            <h2>Quick Actions</h2>
            <button onclick="showCreditAdjustment()">Adjust Credits</button>
            <button onclick="downloadFullReport()">Download Report</button>
            <button onclick="viewAllCompanies()">View All Companies</button>
        </section>
    </main>
    
    <script src="../js/admin.js"></script>
</body>
</html>
```

---

## 🎯 Phase 7: Launch Preparation (Week 7)

### 7.1 Legal Documents ⬜

**Create**: `frontend-simple/legal/terms.html`
- Terms of Service focusing on:
  - IP rights (users retain ownership)
  - Service limitations
  - Payment terms
  - Liability limitations

**Create**: `frontend-simple/legal/privacy.html`
- Privacy Policy covering:
  - Data collection
  - Data usage
  - Data retention (30 days)
  - GDPR compliance

### 7.2 Onboarding Flow ⬜

**Create**: `frontend-simple/onboarding.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Welcome to Image2Model</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="onboarding-container">
        <div class="step" id="step1">
            <h2>Welcome to Image2Model!</h2>
            <p>Transform your 2D images into 3D models with AI</p>
            <button onclick="nextStep()">Get Started</button>
        </div>
        
        <div class="step" id="step2" style="display:none;">
            <h2>How It Works</h2>
            <ol>
                <li>Upload your images (JPG, PNG)</li>
                <li>Our AI processes them into 3D models</li>
                <li>Download your GLB files</li>
            </ol>
            <button onclick="nextStep()">Continue</button>
        </div>
        
        <div class="step" id="step3" style="display:none;">
            <h2>Your Free Credits</h2>
            <p>You start with 100 free credits!</p>
            <p>Each image uses 35-70 credits depending on quality.</p>
            <button onclick="completeOnboarding()">Start Creating</button>
        </div>
    </div>
    <script src="js/onboarding.js"></script>
</body>
</html>
```

### 7.3 Monitoring Setup ⬜

**Sentry Integration**:
```python
# In main.py
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.ENVIRONMENT,
    traces_sample_rate=0.1,
)

app = FastAPI()
app.add_middleware(SentryAsgiMiddleware)
```

**Health Check Enhancement**:
```python
# In health.py
@router.get("/health/detailed")
async def detailed_health(db: Session = Depends(get_db)):
    checks = {
        "database": check_database(db),
        "redis": check_redis(),
        "fal_api": check_fal_api(),
        "disk_space": check_disk_space(),
        "credit_system": check_credit_system(db)
    }
    
    status = "healthy" if all(checks.values()) else "unhealthy"
    return {"status": status, "checks": checks}
```

---

## 📊 Implementation Timeline

### Week 1-2: Foundation ⬜
- [ ] Database schema and models
- [ ] Basic authentication
- [ ] User isolation
- [ ] Frontend auth pages

### Week 3: Usage Tracking ⬜
- [ ] Credit system
- [ ] Usage logging
- [ ] Dashboard
- [ ] Email notifications

### Week 4: Company Features ⬜
- [ ] Company admin panel
- [ ] User invitations
- [ ] File isolation
- [ ] Usage reports

### Week 5: Production ⬜
- [ ] Security hardening
- [ ] Cloudflare deployment
- [ ] Backup system
- [ ] Monitoring

### Week 6: Billing (Optional) ⬜
- [ ] Stripe integration
- [ ] Payment flows
- [ ] Invoice generation
- [ ] Subscription management

### Week 7: Launch ⬜
- [ ] Legal documents
- [ ] Onboarding flow
- [ ] Admin tools
- [ ] Beta testing

---

## 🎯 Revenue Model

### Pricing Structure
- **Base Fee**: $10/user/month (includes 100 credits)
- **Additional Credits**: 
  - 100 credits = $50
  - 500 credits = $200 (20% discount)
  - 1000 credits = $350 (30% discount)

### Credit Usage
- Low quality (1000 faces): 35 credits
- Medium quality (5000 faces): 52 credits  
- High quality (10000 faces): 70 credits

### Example Monthly Revenue (10 users)
- Base fees: 10 × $10 = $100
- Additional credits: ~$200
- **Total Revenue**: ~$300/month
- **FAL.AI Costs**: ~$85
- **Profit**: ~$215 (71% margin)

---

## 🚨 Critical Success Factors

1. **Start Simple**: Manual credit top-ups initially
2. **Security First**: File isolation is critical
3. **Monitor Costs**: Track FAL.AI usage closely
4. **User Experience**: Fast processing, clear pricing
5. **Support**: Quick response to issues
6. **Gradual Rollout**: Test with one company first

---

## 📝 Notes

- All code examples are templates - adjust for your specific needs
- Test thoroughly in staging before production
- Keep backups of everything
- Monitor costs daily initially
- Get user feedback early and often

**Document Version**: 1.0  
**Last Updated**: [Current Date]  
**Next Review**: After Phase 1 completion