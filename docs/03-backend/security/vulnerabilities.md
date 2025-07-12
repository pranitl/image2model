# Security Vulnerabilities and Mitigation

## Overview

This document identifies potential security vulnerabilities in the Image2Model backend and provides mitigation strategies. Understanding these vulnerabilities helps maintain a secure system.

## Current Vulnerabilities

### 1. API Key Timing Attack

**Vulnerability:**
```python
# Current vulnerable implementation
if credentials.credentials != settings.API_KEY:
    raise HTTPException(status_code=403)
```

Direct string comparison is vulnerable to timing attacks where attackers can measure response time to guess the API key character by character.

**Risk Level:** Medium

**Mitigation:**
```python
import hmac

def secure_compare(a: str, b: str) -> bool:
    """Constant-time string comparison"""
    return hmac.compare_digest(a.encode(), b.encode())

# Secure implementation
if not secure_compare(credentials.credentials, settings.API_KEY):
    raise HTTPException(status_code=403)
```

### 2. Missing Security Headers

**Vulnerability:**
The application doesn't set important security headers, leaving it vulnerable to various attacks.

**Risk Level:** Medium

**Current State:**
- No X-Frame-Options header (Clickjacking risk)
- No Content-Security-Policy (XSS risk)
- No X-Content-Type-Options (MIME sniffing risk)

**Mitigation:**
```python
from fastapi import Request
from fastapi.responses import Response

@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    
    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # Enable XSS filter
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Force HTTPS
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Content Security Policy
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
    
    # Referrer Policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Permissions Policy
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response
```

### 3. File Upload Vulnerabilities

**Vulnerability:**
Current file validation only checks content-type header and extension, which can be spoofed.

**Risk Level:** High

**Attack Vectors:**
- Malicious file upload with spoofed MIME type
- ZIP bombs
- Polyglot files
- Path traversal in filenames

**Mitigation:**
```python
import magic
import zipfile
import tempfile

class SecureFileValidator:
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_DECOMPRESSED_SIZE = 100 * 1024 * 1024  # 100MB
    
    @staticmethod
    def validate_image_file(file_content: bytes, filename: str) -> bool:
        """Comprehensive file validation"""
        
        # 1. Check magic bytes (not just headers)
        file_type = magic.from_buffer(file_content, mime=True)
        if not file_type.startswith('image/'):
            raise SecurityError("Invalid file type detected")
        
        # 2. Check for embedded archives (ZIP bombs)
        if SecureFileValidator._is_archive(file_content):
            raise SecurityError("Archive files not allowed")
        
        # 3. Validate image integrity
        try:
            from PIL import Image
            import io
            
            img = Image.open(io.BytesIO(file_content))
            img.verify()  # Verify image integrity
            
            # Check image dimensions to prevent DoS
            if img.width * img.height > 50000000:  # 50 megapixels
                raise SecurityError("Image dimensions too large")
                
        except Exception as e:
            raise SecurityError(f"Invalid image file: {str(e)}")
        
        # 4. Sanitize filename
        safe_filename = SecureFileValidator._sanitize_filename(filename)
        
        return True
    
    @staticmethod
    def _is_archive(content: bytes) -> bool:
        """Check if file is an archive"""
        archive_signatures = [
            b'PK\x03\x04',  # ZIP
            b'PK\x05\x06',  # ZIP
            b'PK\x07\x08',  # ZIP
            b'\x1f\x8b\x08',  # GZIP
            b'BZh',  # BZIP2
            b'\xfd7zXZ\x00',  # XZ
        ]
        
        return any(content.startswith(sig) for sig in archive_signatures)
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Remove dangerous characters from filename"""
        # Remove path separators and null bytes
        dangerous_chars = ['/', '\\', '\x00', '..']
        safe_name = filename
        
        for char in dangerous_chars:
            safe_name = safe_name.replace(char, '')
        
        # Only allow alphanumeric, dash, underscore, and dot
        import re
        safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', safe_name)
        
        # Limit length
        name, ext = os.path.splitext(safe_name)
        if len(name) > 50:
            name = name[:50]
        
        return f"{name}{ext}"
```

### 4. Unencrypted File Storage

**Vulnerability:**
Uploaded files and generated models are stored unencrypted on disk.

**Risk Level:** High

**Impact:**
- Data breach if server is compromised
- No protection for sensitive images
- Compliance issues (GDPR, HIPAA)

**Mitigation:**
```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class EncryptedStorage:
    def __init__(self, master_key: str):
        # Derive encryption key from master key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'stable_salt',  # Should use unique salt per file
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        self.cipher = Fernet(key)
    
    async def store_file(self, file_path: Path, content: bytes) -> Path:
        """Store file with encryption"""
        # Encrypt content
        encrypted_content = self.cipher.encrypt(content)
        
        # Store with .enc extension
        encrypted_path = file_path.with_suffix(file_path.suffix + '.enc')
        
        async with aiofiles.open(encrypted_path, 'wb') as f:
            await f.write(encrypted_content)
        
        # Store metadata
        metadata = {
            'original_name': file_path.name,
            'encrypted_at': datetime.utcnow().isoformat(),
            'size': len(content)
        }
        
        metadata_path = encrypted_path.with_suffix('.meta')
        async with aiofiles.open(metadata_path, 'w') as f:
            await f.write(json.dumps(metadata))
        
        return encrypted_path
    
    async def retrieve_file(self, encrypted_path: Path) -> bytes:
        """Retrieve and decrypt file"""
        async with aiofiles.open(encrypted_path, 'rb') as f:
            encrypted_content = await f.read()
        
        return self.cipher.decrypt(encrypted_content)
```

### 5. Redis Security

**Vulnerability:**
Redis instance has no authentication and stores sensitive data in plain text.

**Risk Level:** High

**Issues:**
- No password protection
- No encryption for data at rest
- No TLS for data in transit
- API keys stored in plain text

**Mitigation:**
```python
# Redis configuration with security
import redis
from redis.sentinel import Sentinel

class SecureRedisClient:
    def __init__(self):
        # Use Redis Sentinel for HA and security
        self.sentinel = Sentinel([
            ('sentinel1', 26379),
            ('sentinel2', 26379),
            ('sentinel3', 26379)
        ], password=settings.REDIS_SENTINEL_PASSWORD)
        
        # Get master with authentication
        self.master = self.sentinel.master_for(
            'mymaster',
            password=settings.REDIS_PASSWORD,
            socket_connect_timeout=0.1,
            decode_responses=True,
            ssl=True,
            ssl_cert_reqs='required',
            ssl_ca_certs='/path/to/ca.pem'
        )
    
    async def store_sensitive(self, key: str, value: dict, ttl: int = 3600):
        """Store sensitive data with encryption"""
        # Encrypt value before storing
        encrypted_value = self.encrypt_data(json.dumps(value))
        
        # Use pipeline for atomic operations
        pipe = self.master.pipeline()
        pipe.setex(key, ttl, encrypted_value)
        pipe.execute()
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt data before storing in Redis"""
        cipher = Fernet(settings.REDIS_ENCRYPTION_KEY)
        return cipher.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data from Redis"""
        cipher = Fernet(settings.REDIS_ENCRYPTION_KEY)
        return cipher.decrypt(encrypted_data.encode()).decode()
```

### 6. Insufficient Rate Limiting

**Vulnerability:**
Current rate limiting is IP-based only and can be bypassed using proxies.

**Risk Level:** Medium

**Issues:**
- No per-API-key rate limiting
- No distributed rate limiting
- Can be bypassed with X-Forwarded-For spoofing

**Mitigation:**
```python
from typing import Optional
import hashlib

class EnhancedRateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def check_rate_limit(
        self,
        request: Request,
        api_key: Optional[str] = None,
        limit: int = 60,
        window: int = 60
    ) -> bool:
        """Multi-factor rate limiting"""
        
        # 1. API key-based limiting (primary)
        if api_key:
            key = f"rl:key:{hashlib.sha256(api_key.encode()).hexdigest()[:16]}"
            if not await self._check_limit(key, limit, window):
                return False
        
        # 2. IP-based limiting (secondary)
        ip = self._get_real_ip(request)
        ip_key = f"rl:ip:{ip}"
        ip_limit = limit * 2  # More lenient for IP
        
        if not await self._check_limit(ip_key, ip_limit, window):
            return False
        
        # 3. Global rate limiting (prevent DoS)
        global_key = "rl:global"
        global_limit = limit * 100  # Total system limit
        
        if not await self._check_limit(global_key, global_limit, window):
            logger.warning("Global rate limit reached")
            return False
        
        return True
    
    def _get_real_ip(self, request: Request) -> str:
        """Get real IP with spoofing protection"""
        # Trust only specific proxies
        trusted_proxies = {'10.0.0.1', '10.0.0.2'}
        
        client_ip = request.client.host
        
        # Only trust X-Forwarded-For from trusted proxies
        if client_ip in trusted_proxies:
            forwarded = request.headers.get('X-Forwarded-For')
            if forwarded:
                # Take the first IP (original client)
                return forwarded.split(',')[0].strip()
        
        return client_ip
    
    async def _check_limit(self, key: str, limit: int, window: int) -> bool:
        """Check single rate limit"""
        try:
            current = await self.redis.incr(key)
            
            if current == 1:
                await self.redis.expire(key, window)
            
            if current > limit:
                ttl = await self.redis.ttl(key)
                logger.warning(f"Rate limit exceeded for {key}, retry after {ttl}s")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # Fail open to prevent service disruption
            return True
```

### 7. Logging Sensitive Data

**Vulnerability:**
Application logs may contain sensitive information like API keys, file contents, or user data.

**Risk Level:** Medium

**Mitigation:**
```python
import re
from typing import Any, Dict

class SecureLogger:
    SENSITIVE_PATTERNS = [
        (re.compile(r'api[_-]?key["\']?\s*[:=]\s*["\']?([^"\'\s]+)', re.I), 'API_KEY'),
        (re.compile(r'authorization:\s*bearer\s+(\S+)', re.I), 'AUTH_TOKEN'),
        (re.compile(r'password["\']?\s*[:=]\s*["\']?([^"\'\s]+)', re.I), 'PASSWORD'),
        (re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'), 'CREDIT_CARD'),
        (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), 'EMAIL'),
    ]
    
    @classmethod
    def sanitize(cls, message: str) -> str:
        """Remove sensitive data from log messages"""
        sanitized = message
        
        for pattern, label in cls.SENSITIVE_PATTERNS:
            sanitized = pattern.sub(f'[REDACTED-{label}]', sanitized)
        
        return sanitized
    
    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize dictionary"""
        sanitized = {}
        
        sensitive_keys = {
            'password', 'api_key', 'token', 'secret',
            'authorization', 'auth', 'credential'
        }
        
        for key, value in data.items():
            if any(s in key.lower() for s in sensitive_keys):
                sanitized[key] = '[REDACTED]'
            elif isinstance(value, dict):
                sanitized[key] = cls.sanitize_dict(value)
            elif isinstance(value, str):
                sanitized[key] = cls.sanitize(value)
            else:
                sanitized[key] = value
        
        return sanitized

# Custom logging formatter
class SecureFormatter(logging.Formatter):
    def format(self, record):
        # Sanitize the message
        record.msg = SecureLogger.sanitize(str(record.msg))
        
        # Sanitize extra fields
        if hasattr(record, '__dict__'):
            for key, value in record.__dict__.items():
                if isinstance(value, str):
                    setattr(record, key, SecureLogger.sanitize(value))
        
        return super().format(record)
```

## Vulnerability Scanning

### Automated Security Scanning

```python
# Integration with security scanning tools
class SecurityScanner:
    async def scan_dependencies(self):
        """Scan Python dependencies for vulnerabilities"""
        # Use safety or pip-audit
        result = subprocess.run(
            ['safety', 'check', '--json'],
            capture_output=True,
            text=True
        )
        
        vulnerabilities = json.loads(result.stdout)
        return vulnerabilities
    
    async def scan_code(self):
        """Static code analysis for security issues"""
        # Use bandit for Python security linting
        result = subprocess.run(
            ['bandit', '-r', '.', '-f', 'json'],
            capture_output=True,
            text=True
        )
        
        issues = json.loads(result.stdout)
        return issues
```

## Security Testing

### Penetration Testing Checklist

- [ ] SQL Injection attempts
- [ ] XSS in file uploads
- [ ] Path traversal attacks
- [ ] API key brute force
- [ ] Rate limit bypass
- [ ] File upload exploits
- [ ] Session hijacking
- [ ] CSRF attacks
- [ ] XXE attacks
- [ ] DoS attempts

### Security Test Suite

```python
import pytest
from httpx import AsyncClient

class TestSecurity:
    @pytest.mark.asyncio
    async def test_sql_injection(self, client: AsyncClient):
        """Test SQL injection prevention"""
        payloads = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users--"
        ]
        
        for payload in payloads:
            response = await client.get(
                f"/api/v1/status/{payload}"
            )
            
            # Should reject malicious input
            assert response.status_code in [400, 404]
            assert "error" in response.json()
    
    @pytest.mark.asyncio
    async def test_path_traversal(self, client: AsyncClient):
        """Test path traversal prevention"""
        payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "....//....//....//etc/passwd"
        ]
        
        for payload in payloads:
            response = await client.get(
                f"/api/v1/download/job123/{payload}/model"
            )
            
            assert response.status_code in [400, 403, 404]
```

## Incident Response Plan

### Security Incident Workflow

1. **Detection** - Automated alerts or manual discovery
2. **Assessment** - Determine severity and scope
3. **Containment** - Isolate affected systems
4. **Eradication** - Remove threat
5. **Recovery** - Restore normal operations
6. **Lessons Learned** - Post-incident review

### Automated Response

```python
class SecurityIncidentHandler:
    async def handle_incident(self, incident_type: str, details: dict):
        """Automated incident response"""
        
        # 1. Log the incident
        logger.critical(f"Security incident: {incident_type}", extra=details)
        
        # 2. Take immediate action
        if incident_type == "brute_force_attack":
            await self.block_attacker(details['source_ip'])
        elif incident_type == "data_breach":
            await self.lockdown_system()
        
        # 3. Notify administrators
        await self.send_alert(incident_type, details)
        
        # 4. Preserve evidence
        await self.capture_forensics(details)
```