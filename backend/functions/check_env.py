"""
Diagnose environment variables
"""
import os

print("Environment Variables Check:")
print("=" * 60)

# Check all relevant env vars
env_vars = [
    'FRED_API_KEY',
    'GCP_PROJECT_ID',
    'GOOGLE_APPLICATION_CREDENTIALS'
]

for var in env_vars:
    value = os.getenv(var)
    if value:
        # Mask sensitive values
        if 'KEY' in var or 'CREDENTIALS' in var:
            display = value[:10] + '...' if len(value) > 10 else '***'
        else:
            display = value
        print(f"✓ {var}: {display}")
    else:
        print(f"✗ {var}: Not Set")

print("\n" + "=" * 60)
print("All environment variables:")
print("=" * 60)

# Show all env vars that might be relevant
for key, value in os.environ.items():
    if any(x in key.upper() for x in ['FRED', 'GCP', 'GOOGLE', 'BQ']):
        display = value[:50] + '...' if len(value) > 50 else value
        print(f"{key}: {display}")
