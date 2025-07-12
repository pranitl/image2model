# Rate Limiting Guide

## Overview

The Image2Model API implements rate limiting to ensure fair usage and protect system resources. This guide explains the rate limiting policies, headers, and best practices for handling rate limits.

## Rate Limit Policies

### Default Limits

| Limit Type | Value | Window | Scope |
|------------|-------|--------|-------|
| Per Minute | 60 requests | 1 minute | Per IP Address |
| Per Hour | 1000 requests | 1 hour | Per IP Address |

### Endpoint-Specific Limits

Rate limits are configured via environment variables and applied via decorators:

| Configuration | Default | Description |
|---------------|---------|-------------|
| `RATE_LIMIT_PER_MINUTE` | 60 | Default requests per minute |
| `RATE_LIMIT_PER_HOUR` | 1000 | Default requests per hour |

**Current Implementation**: 
- Upload endpoints use `upload_rate_limit` decorator
- No endpoint-specific custom limits currently implemented
- All endpoints inherit default rate limits from settings

## Rate Limit Headers

All API responses include rate limit information:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1710500000
```

### Header Definitions

- **X-RateLimit-Limit**: Maximum requests allowed in the window
- **X-RateLimit-Remaining**: Requests remaining in current window
- **X-RateLimit-Reset**: Unix timestamp when the window resets

## Implementation Details

### SlowAPI Implementation

The API uses SlowAPI (FastAPI-compatible rate limiter):

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

# Create limiter instance
limiter = Limiter(key_func=get_remote_address)

# Applied to FastAPI app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

### Rate Limit Key

Rate limits are applied based on:
1. IP Address (primary via SlowAPI)
2. Per-endpoint limits via decorators

**Note**: The current implementation uses IP-based limiting via SlowAPI's `get_remote_address`. API key-based limiting is not currently implemented but would be a future enhancement.

```python
from slowapi.util import get_remote_address

# Current implementation uses IP address
limiter = Limiter(key_func=get_remote_address)

# Applied via decorators
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def endpoint():
    pass
```

## Handling Rate Limits

### Rate Limit Response

When rate limit is exceeded:

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1710500000
Retry-After: 60

{
  "error": true,
  "error_code": "RATE_LIMIT_EXCEEDED", 
  "message": "Rate limit exceeded: 60 per 1 minute",
  "details": {
    "limit": "60 per 1 minute",
    "retry_after": 60
  }
}
```

### Client Implementation

#### Python Example

```python
import requests
import time
from datetime import datetime

class RateLimitedClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.rate_limit_remaining = None
        self.rate_limit_reset = None
    
    def request(self, method, url, **kwargs):
        # Check if we should wait before making request
        if self.rate_limit_remaining == 0 and self.rate_limit_reset:
            wait_time = self.rate_limit_reset - time.time()
            if wait_time > 0:
                print(f"Rate limited. Waiting {wait_time:.0f} seconds...")
                time.sleep(wait_time)
        
        # Make request
        response = requests.request(
            method, url, headers=self.headers, **kwargs
        )
        
        # Update rate limit info
        self.rate_limit_remaining = int(
            response.headers.get('X-RateLimit-Remaining', 1)
        )
        self.rate_limit_reset = int(
            response.headers.get('X-RateLimit-Reset', 0)
        )
        
        # Handle rate limit error
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"Rate limited. Retry after {retry_after} seconds")
            time.sleep(retry_after)
            return self.request(method, url, **kwargs)
        
        return response
```

#### JavaScript Example

```javascript
class RateLimitedClient {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.rateLimitRemaining = null;
    this.rateLimitReset = null;
  }
  
  async request(url, options = {}) {
    // Add auth header
    options.headers = {
      ...options.headers,
      'Authorization': `Bearer ${this.apiKey}`
    };
    
    // Check if we should wait
    if (this.rateLimitRemaining === 0 && this.rateLimitReset) {
      const waitTime = (this.rateLimitReset * 1000) - Date.now();
      if (waitTime > 0) {
        console.log(`Rate limited. Waiting ${waitTime}ms...`);
        await new Promise(resolve => setTimeout(resolve, waitTime));
      }
    }
    
    // Make request
    const response = await fetch(url, options);
    
    // Update rate limit info
    this.rateLimitRemaining = parseInt(
      response.headers.get('X-RateLimit-Remaining') || '1'
    );
    this.rateLimitReset = parseInt(
      response.headers.get('X-RateLimit-Reset') || '0'
    );
    
    // Handle rate limit
    if (response.status === 429) {
      const retryAfter = parseInt(
        response.headers.get('Retry-After') || '60'
      );
      console.log(`Rate limited. Retry after ${retryAfter}s`);
      await new Promise(resolve => 
        setTimeout(resolve, retryAfter * 1000)
      );
      return this.request(url, options);
    }
    
    return response;
  }
}
```

## Best Practices

### 1. Implement Request Queuing

Queue requests to avoid hitting rate limits:

```python
from queue import Queue
from threading import Thread
import time

class RequestQueue:
    def __init__(self, requests_per_minute=60):
        self.queue = Queue()
        self.delay = 60.0 / requests_per_minute
        self.running = True
        Thread(target=self._process_queue, daemon=True).start()
    
    def _process_queue(self):
        while self.running:
            if not self.queue.empty():
                func, args, kwargs = self.queue.get()
                func(*args, **kwargs)
                time.sleep(self.delay)
            else:
                time.sleep(0.1)
    
    def add_request(self, func, *args, **kwargs):
        self.queue.put((func, args, kwargs))
```

### 2. Use Exponential Backoff

For repeated rate limit errors:

```python
def exponential_backoff(func, max_retries=5):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = min(300, (2 ** attempt) + random.uniform(0, 1))
            time.sleep(wait_time)
```

### 3. Monitor Rate Limit Usage

Track your rate limit consumption:

```python
def log_rate_limit_status(response):
    remaining = response.headers.get('X-RateLimit-Remaining')
    reset = response.headers.get('X-RateLimit-Reset')
    
    if remaining and int(remaining) < 10:
        logging.warning(
            f"Low rate limit: {remaining} requests remaining. "
            f"Resets at {datetime.fromtimestamp(int(reset))}"
        )
```

### 4. Batch Operations

Reduce API calls by batching:

```python
# Instead of:
for image in images:
    api.upload_single(image)  # 100 API calls

# Use:
api.upload_batch(images)  # 1 API call
```

## Rate Limit Strategies

### Development vs Production

#### Development
```python
# Higher limits for testing
RATE_LIMITS = {
    "default": ["120/minute", "2000/hour"],
    "upload": ["20/minute"]
}
```

#### Production
```python
# Conservative limits
RATE_LIMITS = {
    "default": ["60/minute", "1000/hour"],
    "upload": ["10/minute"],
    "admin": ["30/minute"]
}
```

### Per-Tier Rate Limits (Future)

```python
TIER_LIMITS = {
    "free": ["60/minute", "1000/hour"],
    "pro": ["300/minute", "10000/hour"],
    "enterprise": ["1000/minute", "100000/hour"]
}
```

## Monitoring and Alerts

### Metrics to Track

1. **Rate Limit Hits**: Count of 429 responses
2. **Usage Patterns**: Requests per time window
3. **Client Distribution**: Top API key usage
4. **Endpoint Usage**: Most called endpoints

### Alert Conditions

- API key approaching rate limit (>80% usage)
- Repeated rate limit violations
- Unusual traffic patterns
- System-wide rate limit pressure

## Troubleshooting

### Common Issues

#### Issue: Constant Rate Limiting
**Cause**: Making requests too quickly
**Solution**: Implement request queuing and delays

#### Issue: Reset Time Not Updating
**Cause**: Clock synchronization issues
**Solution**: Ensure client and server clocks are synchronized

#### Issue: Different Limits Than Expected
**Cause**: Endpoint-specific limits
**Solution**: Check documentation for endpoint-specific limits

### Debug Headers

Enable debug mode to see additional information:

```http
X-RateLimit-Key: api_key:abc123
X-RateLimit-Window: 60s
X-RateLimit-Policy: default
```

## Future Enhancements

### Planned Features

1. **Dynamic Rate Limiting**: Adjust limits based on system load
2. **Burst Allowance**: Allow short bursts above limit
3. **Priority Queuing**: Higher limits for premium users
4. **Distributed Rate Limiting**: Consistent limits across multiple servers
5. **Cost-Based Limiting**: Limit by resource consumption, not just count