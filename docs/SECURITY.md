# AutoGuard Security Documentation

**Version:** 1.0.0  
**Last Updated:** August 28, 2026  
**Status:** Security Audited ✅

---

## 🔐 Security Overview

AutoGuard has been designed with security-first principles. This document outlines the security features, threat model, and best practices for deployment.

## Security Features Implemented

### 1. Authentication & Authorization

#### Token-Based Authentication
- **Constant-time token comparison** prevents timing attacks
- **Three role levels:** Admin, Security, Viewer
- **Token storage:** Environment variables only (never in code)
- **Session management:** HTTPOnly cookies with 12-hour expiration

#### Security Improvements (Aug 28, 2026)
```python
# Before: Vulnerable to timing attacks
if token == ADMIN_TOKEN:
    allow_access()

# After: Constant-time comparison
if hmac.compare_digest(token, ADMIN_TOKEN):
    allow_access()
```

### 2. Web Application Security

#### Security Headers
All responses include:
- `X-Content-Type-Options: nosniff` - Prevents MIME sniffing
- `X-Frame-Options: DENY` - Prevents clickjacking
- `X-XSS-Protection: 1; mode=block` - Browser XSS filter
- `Strict-Transport-Security` - Forces HTTPS (production)
- `Content-Security-Policy` - Restricts resource loading

#### Cookie Security
- **HTTPOnly flag:** Prevents JavaScript access
- **Secure flag:** HTTPS-only transmission (production)
- **SameSite=Strict:** Prevents CSRF attacks
- **Max-Age:** 12-hour session timeout

#### Input Validation
- **Path traversal prevention:** Strict filename validation
- **No arbitrary paths:** Only filename-based access
- **Character whitelist:** Blocks `..`, `/`, `\` in filenames
- **Directory containment:** `realpath()` verification

### 3. Data Integrity

#### Evidence Verification
Every captured image has:
- **SHA-256 hash** computed at capture time
- **Metadata JSON** with hash, timestamp, camera ID
- **Verification tool** to check integrity

```bash
# Verify all evidence integrity
python -m src.verify_evidence --dir evidence
```

#### Audit Logging
- All detections logged with timestamp
- Evidence capture events recorded
- Alert sending tracked
- Authentication attempts logged

### 4. Infrastructure Security

#### Docker Security
- **Non-root user:** Container runs as `autoguard` (uid 1000)
- **Minimal base image:** Python 3.10-slim
- **No unnecessary privileges:** Standard user permissions
- **Health checks:** Monitors service availability

#### Network Security
- **No public exposure:** Binds to 127.0.0.1 by default
- **Minimal attack surface:** Only necessary ports open
- **Rate limiting:** Prevents brute force attacks

### 5. Dependency Management

#### Package Security
- **Pinned versions** in requirements.txt
- **No wildcard imports** in source code
- **Regular updates:** Check for CVEs monthly
- **Minimal dependencies:** Only essential packages

## Threat Model

### Assets
1. **Evidence files** - Images and metadata of incidents
2. **Credentials** - Authentication tokens, Telegram bot token
3. **Live video feed** - Real-time camera access
4. **System integrity** - Trusted code execution

### Threats Mitigated

| Threat | Mitigation | Status |
|--------|-----------|---------|
| Timing attacks on auth | Constant-time comparison | ✅ Fixed |
| Path traversal | Strict filename validation | ✅ Fixed |
| Token exposure in URLs | Removed from query params | ✅ Fixed |
| Cookie hijacking | HTTPOnly + Secure flags | ✅ Fixed |
| Clickjacking | X-Frame-Options header | ✅ Fixed |
| MIME sniffing | X-Content-Type-Options | ✅ Fixed |
| XSS attacks | CSP headers | ✅ Fixed |
| Container escape | Non-root execution | ✅ Fixed |
| Evidence tampering | SHA-256 verification | ✅ Implemented |
| Brute force | Rate limiting | ✅ Implemented |

### Threats NOT Mitigated (Future Work)
- **CSRF attacks:** No CSRF tokens yet (add Flask-WTF)
- **SQL injection:** Not applicable (no database yet)
- **DDoS:** No distributed rate limiting
- **Physical access:** No device encryption
- **Network sniffing:** Local-only deployment assumed

## Security Best Practices

### Deployment Checklist

#### Before Production
- [ ] Generate strong tokens (32+ characters)
- [ ] Enable HTTPS (remove temp HTTP-only mode)
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Enable audit logging
- [ ] Set evidence retention policy
- [ ] Test backup/restore procedures
- [ ] Document incident response plan

#### Token Generation
```powershell
# Generate cryptographically secure tokens
python -c "import secrets; print('ADMIN_TOKEN=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('SECURITY_TOKEN=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('VIEWER_TOKEN=' + secrets.token_urlsafe(32))"
```

#### Environment Configuration
```env
# .env file - NEVER commit this file!
ADMIN_TOKEN=<64-character-random-token>
SECURITY_TOKEN=<64-character-random-token>
VIEWER_TOKEN=<64-character-random-token>
TELEGRAM_BOT_TOKEN=<your-bot-token>
TELEGRAM_CHAT_IDS=<whitelisted-chat-ids>
CAMERA_ID=CAM01
```

### Network Security

#### Recommended Deployment
```
[Camera] → [AutoGuard Server (localhost only)]
             ↓
[Reverse Proxy (nginx/Apache)]
             ↓
[Firewall]
             ↓
[Authorized Users]
```

#### Nginx Configuration Example
```nginx
server {
    listen 443 ssl http2;
    server_name autoguard.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Access Control

#### Role Permissions

| Action | Admin | Security | Viewer |
|--------|-------|----------|--------|
| View dashboard | ✅ | ✅ | ✅ |
| View evidence | ✅ | ✅ | ✅ |
| View live feed | ✅ | ✅ | ✅ |
| Download images | ✅ | ✅ | ❌ |
| Export evidence | ✅ | ✅ | ❌ |
| Mark resolved | ✅ | ✅ | ❌ |
| Manage devices | ✅ | ❌ | ❌ |
| System config | ✅ | ❌ | ❌ |

#### Token Rotation
Recommended schedule:
- **Admin tokens:** Every 90 days
- **Security tokens:** Every 90 days
- **Viewer tokens:** Every 30 days
- **Telegram bot token:** When exposed or annually

### Data Protection

#### Evidence Storage
- Store in encrypted volume (production)
- Set appropriate file permissions (600 for files, 700 for directories)
- Enable automatic retention policy
- Backup regularly to secure location

#### Sensitive Data
Never log or expose:
- Authentication tokens
- Full file paths
- System internals
- User PII (if any)

### Monitoring & Auditing

#### Log Files
Review regularly:
- `logs/app.log` - Application events
- Evidence JSON files - Detection metadata
- System logs - OS-level events

#### Metrics to Monitor
- Failed authentication attempts
- Evidence capture rate
- System resource usage
- Alert delivery success rate

## Incident Response

### Security Incident Procedure

1. **Detection**
   - Monitor logs for anomalies
   - Check evidence integrity daily
   - Review authentication logs

2. **Containment**
   - Revoke compromised tokens immediately
   - Isolate affected system
   - Block suspicious IPs

3. **Investigation**
   - Review audit logs
   - Verify evidence integrity
   - Identify attack vector

4. **Recovery**
   - Generate new tokens
   - Restore from clean backup if needed
   - Apply patches

5. **Post-Incident**
   - Document lessons learned
   - Update security procedures
   - Train staff on new threats

### Emergency Contacts
```
Security Team: [your-security-email]
System Admin: [your-admin-email]
Incident Response: [your-ir-email]
```

## Compliance

### Privacy Considerations
- **No facial recognition** - System tracks persons, not identities
- **Local processing** - No cloud uploads
- **Controlled access** - Role-based permissions
- **Audit trail** - Complete logs of access

### Data Retention
- **Default:** 7 days (configurable)
- **Minimum:** 1 day
- **Maximum:** 90 days (recommended)
- **Deletion:** Automatic via retention policy

### Legal Requirements
Check local laws regarding:
- Video surveillance notice requirements
- Data retention periods
- Access logs requirements
- Incident reporting obligations

## Security Audit History

### Audit v1.0 (August 28, 2026)
**Auditor:** AutoGuard Development Team  
**Scope:** Full codebase review  
**Status:** ✅ Passed with fixes applied

#### Critical Issues Fixed
1. ✅ Timing attack vulnerability in authentication
2. ✅ Path traversal vulnerability in file access
3. ✅ Token exposure in query parameters
4. ✅ Insecure cookie configuration
5. ✅ Missing security headers
6. ✅ Docker container running as root
7. ✅ Password field showing plain text

#### Recommendations Implemented
- Constant-time token comparison
- Strict filename validation
- Secure cookie configuration
- Security headers middleware
- Non-root Docker user
- Password input masking

## Vulnerability Disclosure

Found a security issue? Please report responsibly:

1. **DO NOT** open public GitHub issues for security bugs
2. Email: [your-security-email] with details
3. Include: Description, steps to reproduce, impact assessment
4. Allow 48 hours for initial response
5. We will coordinate disclosure timeline with you

## Security Maintenance

### Regular Tasks

**Daily:**
- Monitor logs for anomalies
- Check alert delivery

**Weekly:**
- Review evidence integrity
- Check system resource usage
- Backup configuration

**Monthly:**
- Review access logs
- Check for dependency updates
- Test backup restoration

**Quarterly:**
- Rotate authentication tokens
- Security audit
- Penetration testing (if applicable)

**Annually:**
- Full security review
- Update threat model
- Staff security training

---

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)
- [Docker Security Guide](https://docs.docker.com/engine/security/)
- [Python Security Guidelines](https://python.readthedocs.io/en/stable/library/security_warnings.html)

---

**Document Version:** 1.0  
**Last Review:** August 28, 2026  
**Next Review:** November 28, 2026
