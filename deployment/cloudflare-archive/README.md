# Cloudflare Access Scripts

These scripts help manage Cloudflare Access applications for the Image2Model project.

## Setup

All scripts require the `CLOUDFLARE_API_TOKEN` environment variable. You can either:

1. Export it in your shell:
```bash
export CLOUDFLARE_API_TOKEN='your-token-here'
```

2. Or source it from .env.production:
```bash
source .env.production
```

## Scripts

- `check-cloudflare-access.py` - List existing Access applications
- `setup-cloudflare-access-v2.py` - Create new Access applications
- `update-cloudflare-app.py` - Update existing applications
- `check-app-details.py` - Get detailed app configuration
- `verify-cloudflare-token.py` - Verify API token permissions

## Usage Example

```bash
# Check existing apps
python3 check-cloudflare-access.py

# Update app configuration
python3 update-cloudflare-app.py
```