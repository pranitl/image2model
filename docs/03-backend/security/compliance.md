# Data Protection and Compliance

## Overview

This document outlines data protection measures and compliance considerations for the Image2Model backend, covering GDPR, privacy regulations, and industry best practices.

## Data Privacy Principles

### 1. Data Minimization
- Collect only necessary data for 3D model generation
- No persistent storage of personal information
- Automatic data expiration after 24 hours

### 2. Purpose Limitation
- Data used solely for 3D model generation
- No secondary usage without explicit consent
- Clear data processing boundaries

### 3. Transparency
- Clear privacy policy
- Data processing notifications
- Audit trails for data access

## GDPR Compliance

### Data Subject Rights

```python
from enum import Enum
from typing import Optional, List
import asyncio

class DataSubjectRights:
    """Handle GDPR data subject requests"""
    
    class RequestType(Enum):
        ACCESS = "access"
        RECTIFICATION = "rectification"
        ERASURE = "erasure"
        PORTABILITY = "portability"
        RESTRICTION = "restriction"
    
    def __init__(self, redis_client, storage_manager):
        self.redis = redis_client
        self.storage = storage_manager
    
    async def handle_access_request(self, api_key: str) -> dict:
        """Right to Access - Article 15 GDPR"""
        # Get all data associated with API key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        data = {
            "request_date": datetime.utcnow().isoformat(),
            "data_categories": {
                "jobs": [],
                "files": [],
                "models": []
            }
        }
        
        # Find all jobs for this API key
        jobs = await self.redis.smembers(f"user_jobs:{key_hash}")
        
        for job_id in jobs:
            job_data = await self.redis.get(f"job:{job_id}")
            if job_data:
                # Sanitize sensitive information
                job_info = json.loads(job_data)
                job_info.pop('api_key', None)
                data["data_categories"]["jobs"].append(job_info)
                
                # Get associated files
                for file in job_info.get('files', []):
                    file_path = self.storage.get_file_path(job_id, file['id'])
                    if file_path.exists():
                        data["data_categories"]["files"].append({
                            "filename": file['filename'],
                            "size": file_path.stat().st_size,
                            "created": file_path.stat().st_ctime
                        })
        
        return data
    
    async def handle_erasure_request(self, api_key: str) -> dict:
        """Right to Erasure - Article 17 GDPR"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        deleted_items = {
            "jobs": 0,
            "files": 0,
            "redis_keys": 0
        }
        
        # Get all jobs for this API key
        jobs = await self.redis.smembers(f"user_jobs:{key_hash}")
        
        for job_id in jobs:
            # Delete files
            job_dir = self.storage.get_job_directory(job_id)
            if job_dir.exists():
                for file in job_dir.iterdir():
                    # Secure deletion
                    await self.secure_delete_file(file)
                    deleted_items["files"] += 1
                
                # Remove directory
                job_dir.rmdir()
            
            # Delete from Redis
            keys_to_delete = await self.redis.keys(f"*{job_id}*")
            if keys_to_delete:
                await self.redis.delete(*keys_to_delete)
                deleted_items["redis_keys"] += len(keys_to_delete)
            
            deleted_items["jobs"] += 1
        
        # Delete user's job list
        await self.redis.delete(f"user_jobs:{key_hash}")
        
        # Log the deletion
        logger.info(
            "Data erasure completed",
            api_key_hash=key_hash[:8],
            deleted_items=deleted_items
        )
        
        return {
            "status": "completed",
            "deleted": deleted_items,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def handle_portability_request(self, api_key: str) -> bytes:
        """Right to Data Portability - Article 20 GDPR"""
        # Get all user data
        user_data = await self.handle_access_request(api_key)
        
        # Create ZIP file with all data
        import zipfile
        import io
        
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add JSON metadata
            zip_file.writestr(
                'metadata.json',
                json.dumps(user_data, indent=2)
            )
            
            # Add files
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            jobs = await self.redis.smembers(f"user_jobs:{key_hash}")
            
            for job_id in jobs:
                job_dir = self.storage.get_job_directory(job_id)
                if job_dir.exists():
                    for file in job_dir.iterdir():
                        if file.is_file():
                            zip_file.write(file, f"{job_id}/{file.name}")
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
    
    @staticmethod
    async def secure_delete_file(file_path: Path):
        """Securely overwrite and delete file"""
        if not file_path.exists():
            return
        
        file_size = file_path.stat().st_size
        
        # Overwrite with random data 3 times
        for _ in range(3):
            with open(file_path, 'ba+') as f:
                f.write(os.urandom(file_size))
                f.flush()
                os.fsync(f.fileno())
        
        # Delete file
        file_path.unlink()
```

### Privacy by Design

```python
class PrivacyByDesign:
    """Implement privacy by design principles"""
    
    @staticmethod
    def anonymize_logs(log_entry: dict) -> dict:
        """Remove PII from logs"""
        # IP anonymization
        if 'ip_address' in log_entry:
            ip = log_entry['ip_address']
            # Keep only first 3 octets for IPv4
            if '.' in ip:
                parts = ip.split('.')
                parts[3] = '0'
                log_entry['ip_address'] = '.'.join(parts)
            # Anonymize IPv6
            elif ':' in ip:
                log_entry['ip_address'] = ip.rsplit(':', 1)[0] + ':0000'
        
        # Remove user agent details
        if 'user_agent' in log_entry:
            # Keep only browser and OS
            ua = log_entry['user_agent']
            log_entry['user_agent'] = PrivacyByDesign._simplify_user_agent(ua)
        
        # Hash identifiers
        if 'api_key' in log_entry:
            log_entry['api_key'] = hashlib.sha256(
                log_entry['api_key'].encode()
            ).hexdigest()[:8]
        
        return log_entry
    
    @staticmethod
    def _simplify_user_agent(ua: str) -> str:
        """Extract only browser and OS from user agent"""
        # Simple extraction - in production use a proper UA parser
        if 'Chrome' in ua:
            browser = 'Chrome'
        elif 'Firefox' in ua:
            browser = 'Firefox'
        elif 'Safari' in ua:
            browser = 'Safari'
        else:
            browser = 'Other'
        
        if 'Windows' in ua:
            os = 'Windows'
        elif 'Mac' in ua:
            os = 'MacOS'
        elif 'Linux' in ua:
            os = 'Linux'
        else:
            os = 'Other'
        
        return f"{browser}/{os}"
```

### Data Processing Records

```python
class DataProcessingRegistry:
    """Maintain records of processing activities - Article 30 GDPR"""
    
    def __init__(self):
        self.processing_activities = {
            "image_to_3d_conversion": {
                "purpose": "Convert 2D images to 3D models for users",
                "categories_of_data": [
                    "Uploaded images",
                    "API keys for authentication",
                    "IP addresses for rate limiting",
                    "Generated 3D models"
                ],
                "categories_of_recipients": [
                    "FAL.AI (third-party processor)",
                    "CDN providers (for model delivery)"
                ],
                "retention_period": "24 hours",
                "security_measures": [
                    "Encryption in transit (TLS)",
                    "API key authentication",
                    "Rate limiting",
                    "Automatic data deletion"
                ],
                "transfers_outside_eu": True,
                "transfer_safeguards": "Standard Contractual Clauses with processors"
            }
        }
    
    def generate_article_30_record(self) -> dict:
        """Generate Article 30 compliance record"""
        return {
            "controller": {
                "name": "Image2Model Service",
                "contact": "privacy@image2model.com",
                "representative": "EU Representative Ltd"
            },
            "processing_activities": self.processing_activities,
            "last_updated": datetime.utcnow().isoformat()
        }
```

## Security Compliance

### OWASP Top 10 Mitigation

```python
class OWASPCompliance:
    """Implement OWASP Top 10 security controls"""
    
    # A01:2021 – Broken Access Control
    @staticmethod
    async def enforce_access_control(user_id: str, resource_id: str) -> bool:
        """Enforce proper access control"""
        # Implement principle of least privilege
        # Check ownership before granting access
        return await session_store.verify_ownership(resource_id, user_id)
    
    # A02:2021 – Cryptographic Failures
    @staticmethod
    def use_strong_cryptography():
        """Ensure strong cryptographic practices"""
        return {
            "tls_version": "1.2+",
            "cipher_suites": [
                "TLS_AES_256_GCM_SHA384",
                "TLS_CHACHA20_POLY1305_SHA256"
            ],
            "key_length": 256,
            "hash_algorithm": "SHA-256",
            "password_hashing": "bcrypt with cost 12"
        }
    
    # A03:2021 – Injection
    @staticmethod
    def prevent_injection(user_input: str) -> str:
        """Prevent injection attacks"""
        # Parameterized queries (when using SQL)
        # Input validation
        # Output encoding
        
        # Whitelist validation for job IDs
        if not re.match(r'^[a-zA-Z0-9_-]+$', user_input):
            raise ValidationError("Invalid input format")
        
        return user_input
    
    # A04:2021 – Insecure Design
    @staticmethod
    def secure_design_checklist():
        """Security design requirements"""
        return {
            "threat_modeling": "Complete",
            "secure_design_patterns": ["Authentication", "Authorization", "Input Validation"],
            "security_requirements": "Documented",
            "secure_coding_guidelines": "Enforced"
        }
```

### PCI DSS Considerations

```python
class PCICompliance:
    """PCI DSS compliance measures (if payment processing is added)"""
    
    @staticmethod
    def tokenize_sensitive_data(card_number: str) -> str:
        """Tokenize payment card data"""
        # Never store actual card numbers
        # Use tokenization service
        return "tok_" + hashlib.sha256(card_number.encode()).hexdigest()[:16]
    
    @staticmethod
    def implement_pci_controls():
        """PCI DSS control implementation"""
        return {
            "network_segmentation": True,
            "encryption_at_rest": True,
            "encryption_in_transit": True,
            "access_logging": True,
            "vulnerability_scanning": "Quarterly",
            "penetration_testing": "Annual",
            "security_training": "Annual"
        }
```

## Audit and Monitoring

### Compliance Monitoring

```python
class ComplianceMonitor:
    """Monitor compliance with regulations"""
    
    def __init__(self):
        self.metrics = {
            'data_requests': Counter('gdpr_requests_total', 'GDPR requests', ['type']),
            'retention_violations': Counter('retention_violations_total', 'Data retained too long'),
            'security_incidents': Counter('security_incidents_total', 'Security incidents', ['type'])
        }
    
    async def check_data_retention(self):
        """Ensure data is deleted per retention policy"""
        retention_limit = 24 * 3600  # 24 hours
        
        # Check Redis keys
        keys = await redis.keys("job:*")
        
        for key in keys:
            ttl = await redis.ttl(key)
            
            if ttl == -1:  # No expiration set
                logger.error(f"No TTL set for {key}")
                self.metrics['retention_violations'].inc()
                
                # Fix by setting TTL
                await redis.expire(key, retention_limit)
        
        # Check file system
        for job_dir in Path("./uploads").iterdir():
            if job_dir.is_dir():
                age = time.time() - job_dir.stat().st_mtime
                
                if age > retention_limit:
                    logger.warning(f"Old directory found: {job_dir}")
                    self.metrics['retention_violations'].inc()
                    
                    # Schedule for deletion
                    await self.schedule_deletion(job_dir)
    
    async def generate_compliance_report(self) -> dict:
        """Generate compliance status report"""
        return {
            "report_date": datetime.utcnow().isoformat(),
            "gdpr_compliance": {
                "data_retention": await self.check_retention_compliance(),
                "access_controls": await self.check_access_controls(),
                "encryption": await self.check_encryption_status(),
                "audit_logs": await self.check_audit_logs()
            },
            "security_compliance": {
                "vulnerability_scan": await self.last_vulnerability_scan(),
                "penetration_test": await self.last_pentest(),
                "security_training": await self.check_security_training()
            }
        }
```

### Audit Logging

```python
class AuditLogger:
    """Comprehensive audit logging for compliance"""
    
    def __init__(self):
        self.audit_logger = self._setup_audit_logger()
    
    def _setup_audit_logger(self):
        """Configure tamper-evident audit logging"""
        handler = RotatingFileHandler(
            '/secure/audit/audit.log',
            maxBytes=100*1024*1024,  # 100MB
            backupCount=365  # Keep 1 year
        )
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        logger = logging.getLogger('audit')
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        return logger
    
    async def log_data_access(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        success: bool
    ):
        """Log all data access for audit trail"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id_hash": hashlib.sha256(user_id.encode()).hexdigest()[:16],
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action,
            "success": success,
            "correlation_id": str(uuid.uuid4())
        }
        
        # Sign log entry for integrity
        signature = self._sign_log_entry(log_entry)
        log_entry["signature"] = signature
        
        self.audit_logger.info(json.dumps(log_entry))
    
    def _sign_log_entry(self, entry: dict) -> str:
        """Create tamper-evident signature"""
        # In production, use proper digital signatures
        entry_str = json.dumps(entry, sort_keys=True)
        return hashlib.sha256(
            (entry_str + settings.AUDIT_SECRET).encode()
        ).hexdigest()
```

## Privacy Policy Template

```python
def generate_privacy_policy() -> str:
    """Generate privacy policy based on data processing"""
    return """
# Privacy Policy

Last updated: {date}

## Data We Collect
- Images you upload for 3D model generation
- API keys for authentication
- Technical information (IP address for rate limiting)

## How We Use Your Data
- To convert your 2D images into 3D models
- To authenticate your requests
- To prevent abuse of our service

## Data Retention
- All uploaded images and generated models are automatically deleted after 24 hours
- No personal information is stored permanently

## Third-Party Services
- We use FAL.AI for 3D model generation
- Generated models may be temporarily stored on CDN servers

## Your Rights
Under GDPR, you have the right to:
- Access your data
- Correct your data
- Delete your data
- Export your data
- Restrict processing

To exercise these rights, contact: privacy@image2model.com

## Security
We implement industry-standard security measures including:
- Encryption in transit (TLS)
- API key authentication
- Automatic data deletion
- Regular security audits

## Contact
For privacy concerns: privacy@image2model.com
Data Protection Officer: dpo@image2model.com
""".format(date=datetime.utcnow().strftime("%Y-%m-%d"))
```

## Compliance Checklist

### GDPR Compliance
- [ ] Privacy by Design implementation
- [ ] Data Processing Records (Article 30)
- [ ] Data Subject Rights handling
- [ ] Privacy Policy published
- [ ] Cookie consent (if applicable)
- [ ] Data Protection Impact Assessment
- [ ] DPO appointed (if required)

### Security Compliance
- [ ] OWASP Top 10 addressed
- [ ] Regular vulnerability scanning
- [ ] Penetration testing
- [ ] Security training program
- [ ] Incident response plan
- [ ] Business continuity plan

### Operational Compliance
- [ ] Audit logging enabled
- [ ] Data retention enforced
- [ ] Access controls implemented
- [ ] Encryption at rest and in transit
- [ ] Third-party processor agreements
- [ ] Regular compliance audits