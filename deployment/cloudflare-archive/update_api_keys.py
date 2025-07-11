#!/usr/bin/env python3
"""Update all Python files to use environment variables for API keys"""

import os
import re

files_to_update = [
    "update-cloudflare-app.py",
    "check-app-details.py", 
    "setup-cloudflare-access-v2.py",
    "get-account-info.py",
    "verify-cloudflare-token.py",
    "check-cloudflare-access.py",
    "setup-cloudflare-access.py"
]

old_token_line = 'CLOUDFLARE_API_TOKEN = "fpYCRP2bqpwVtuAZ5HJN6scL2gAOBRS6mqfy1-2W"'
old_account_line = 'ACCOUNT_ID = "97bf59a94fce66eee3db3b118c9bb4f1"'

new_imports = """import os

# Configuration from environment
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
if not CLOUDFLARE_API_TOKEN:
    print("Error: CLOUDFLARE_API_TOKEN environment variable not set")
    print("Set it with: export CLOUDFLARE_API_TOKEN='your-token'")
    sys.exit(1)

ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "97bf59a94fce66eee3db3b118c9bb4f1")"""

for filename in files_to_update:
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            content = f.read()
        
        # Check if already has import os
        if "import os" not in content:
            content = content.replace("import sys", "import sys\nimport os")
        
        # Replace the API token line
        content = content.replace(old_token_line, 
            'CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")')
        
        # Replace account ID if it exists as a standalone line
        if 'ACCOUNT_ID = "97bf59a94fce66eee3db3b118c9bb4f1"' in content:
            content = content.replace('ACCOUNT_ID = "97bf59a94fce66eee3db3b118c9bb4f1"',
                'ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "97bf59a94fce66eee3db3b118c9bb4f1")')
        
        # Add error checking after CLOUDFLARE_API_TOKEN assignment
        if 'if not CLOUDFLARE_API_TOKEN:' not in content:
            content = re.sub(
                r'CLOUDFLARE_API_TOKEN = os\.getenv\("CLOUDFLARE_API_TOKEN"\)\n',
                'CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")\nif not CLOUDFLARE_API_TOKEN:\n    print("Error: CLOUDFLARE_API_TOKEN environment variable not set")\n    print("Set it with: export CLOUDFLARE_API_TOKEN=\'your-token\'")\n    sys.exit(1)\n\n',
                content
            )
        
        with open(filename, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated {filename}")

print("\nAll files updated to use environment variables!")
print("\nTo use these scripts, set the environment variable:")
print("export CLOUDFLARE_API_TOKEN='fpYCRP2bqpwVtuAZ5HJN6scL2gAOBRS6mqfy1-2W'")