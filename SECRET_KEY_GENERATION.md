# Secret Key Generation Guide

The `SECRET_KEY` is used for signing JWT tokens and session management. It's critical for security.

## Quick Methods

### Option 1: Python (Recommended)
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Option 2: OpenSSL
```bash
openssl rand -hex 32
```

### Option 3: Using `uv` (if you have it installed)
```bash
uv run python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Best Practices

1. **Length**: Use at least 32 characters (64+ is better)
2. **Randomness**: Use cryptographically secure random generators
3. **Uniqueness**: Generate a unique key for each environment (dev, staging, production)
4. **Storage**: Never commit secrets to version control
5. **Rotation**: Consider rotating keys periodically in production

## Example Output

```
# Example secret key (DO NOT USE THIS - generate your own!)
SECRET_KEY=K8j3mN9pQ2rT5vX8zA1bC4dE7fG0hI3jK6mN9pQ2rT5vX8zA1bC4dE7fG0hI
```

## For Production

- Use environment variables (never hardcode)
- Use a secrets management service (AWS Secrets Manager, HashiCorp Vault, etc.)
- Set different keys for different environments
- Document the key generation method for your team

## Quick Setup Script

You can add this to your setup process:

```bash
# Generate and add to .env
echo "SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" >> .env
```

