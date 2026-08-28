# Security Fixes Applied - Aug 28, 2026

## Critical Issues Fixed

### 1. Authentication Security ✅
- **Added constant-time token comparison** to prevent timing attacks (src/server.py)
- **Removed tokens from query parameters** - only accepting via headers or secure cookies
- **Enhanced cookie security**: Added `Secure`, `HTTPOnly`, `SameSite=Strict` flags with 12-hour expiration
- **Changed login form** to use `type='password'` instead of `type='text'`

### 2. Path Traversal Protection ✅
- **Removed arbitrary path parameter** from `/evidence/image` endpoint
- **Added filename validation** to block `..`, `/`, and `\` characters
- **Enforced strict directory containment** with realpath checks

### 3. Security Headers ✅
Added comprehensive security headers to all responses:
- `X-Content-Type-Options: nosniff` - Prevents MIME sniffing
- `X-Frame-Options: DENY` - Prevents clickjacking
- `X-XSS-Protection: 1; mode=block` - Browser XSS filter
- `Strict-Transport-Security` - Forces HTTPS
- `Content-Security-Policy` - Restricts resource loading

### 4. Docker Security ✅
- **Created non-root user** (`autoguard` uid 1000) in container
- **Set proper file ownership** for application directories
- **Switched to non-root execution** - container no longer runs as root

## Important Notes for Demo

### HTTPS Requirement
The secure cookie flag requires HTTPS. For local testing/demo:

**Option 1: Run without HTTPS (Development Only)**
Temporarily comment out `secure=True` in src/server.py line 125:
```python
resp.set_cookie('auth_token', token, httponly=True, samesite='Strict', max_age=43200)
```

**Option 2: Use HTTPS Proxy**
Run behind nginx or use Flask-Thumper for local HTTPS.

### Token Setup
Make sure to set strong tokens in your `.env` file:
```bash
ADMIN_TOKEN=<generate-strong-random-token>
SECURITY_TOKEN=<generate-strong-random-token>
VIEWER_TOKEN=<generate-strong-random-token>
```

Generate secure tokens with:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Remaining Recommendations (Post-Demo)

For production deployment, consider:
1. Add CSRF protection (Flask-WTF)
2. Implement rate limiting with Redis backend
3. Add failed login attempt tracking
4. Set up proper SSL/TLS certificates
5. Add audit logging for security events
6. Consider MFA for admin accounts
7. Regular dependency updates and vulnerability scanning
8. File upload content validation

## Testing

Test the fixes:
```bash
# Build and run with Docker
docker-compose build
docker-compose up

# Access at http://localhost:5000
# Login with tokens from .env file
```
