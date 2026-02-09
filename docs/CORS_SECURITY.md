# CORS Security Configuration (CRITICAL-003 Fix)

## Overview

This document explains the CORS (Cross-Origin Resource Sharing) security configuration implemented to fix **CRITICAL-003: Overly Permissive CORS Configuration**.

## The Problem

Previously, CORS was configured with default settings that allowed **any origin** to make requests to the API:

```python
CORS(app)  # ❌ INSECURE - Allows all origins
```

This created a significant security risk:
- Any malicious website could make API requests on behalf of users
- User data could be stolen or modified
- No origin restrictions = open door for CSRF attacks

## The Solution

### 1. Environment-Based Configuration

CORS is now configured based on the `FLASK_ENV` and `ALLOWED_ORIGINS` environment variables:

```python
# Development Mode (FLASK_ENV=development)
- Defaults to localhost origins for convenience
- Allows: http://localhost:5173, http://localhost:5555, and 127.0.0.1 variants

# Production Mode (FLASK_ENV=production)
- REQUIRES explicit ALLOWED_ORIGINS configuration
- No defaults - fails safe if not configured
- Must use HTTPS origins in production
```

### 2. Explicit Origin Allowlist

Configure allowed origins in `.env`:

```bash
# Development
FLASK_ENV=development
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5555

# Production
FLASK_ENV=production
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 3. Restricted Methods and Headers

Only necessary HTTP methods and headers are allowed:

```python
methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']  # No TRACE, CONNECT, etc.
allow_headers=['Content-Type', 'Authorization', 'X-CSRF-Token', 'Accept']
```

### 4. Security Headers

Additional security headers are automatically added to all responses:

| Header | Value | Purpose |
|--------|-------|---------|
| `X-Frame-Options` | `SAMEORIGIN` | Prevent clickjacking |
| `X-Content-Type-Options` | `nosniff` | Prevent MIME sniffing |
| `X-XSS-Protection` | `1; mode=block` | Enable browser XSS protection |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Limit referrer information |
| `Content-Security-Policy` | (varies by env) | Prevent XSS and injection attacks |

## Configuration Guide

### Development Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Set development mode:
   ```bash
   FLASK_ENV=development
   ```

3. (Optional) Customize origins:
   ```bash
   ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
   ```

4. Start the server:
   ```bash
   python web/app.py
   ```

### Production Setup

1. Set production mode:
   ```bash
   FLASK_ENV=production
   ```

2. **REQUIRED:** Configure allowed origins with HTTPS:
   ```bash
   ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```

3. Configure other production settings:
   ```bash
   SECRET_KEY=your-long-random-secret-key-here
   DATABASE_PATH=/var/lib/stock-tracker/stock_tracker.db
   ```

4. Ensure HTTPS is enabled (via reverse proxy like nginx or Caddy)

5. Start the server:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5555 web.app:app
   ```

## Security Best Practices

### ✅ DO

- **Always** set `ALLOWED_ORIGINS` in production
- Use HTTPS origins in production (`https://`)
- Include both www and non-www variants if needed
- Keep the origin list as small as possible
- Use specific ports (`:5555`) rather than wildcards
- Test CORS configuration before deploying

### ❌ DON'T

- Use wildcard origins (`*`)
- Use HTTP origins in production
- Allow origins you don't control
- Include trailing slashes in origins
- Use IP addresses (use domains instead)

## Testing CORS Configuration

### 1. Check Allowed Origins

Start the server and check the logs:

```bash
INFO:app:Using CORS origins from environment: ['http://localhost:5173', 'http://localhost:5555']
INFO:app:CORS configured with restricted origins
```

### 2. Test from Browser Console

```javascript
// Should succeed for allowed origins
fetch('http://localhost:5555/health')
  .then(r => r.json())
  .then(d => console.log('Success:', d))
  .catch(e => console.error('Failed:', e));

// Should fail for disallowed origins
// (Open browser on different origin and try the same request)
```

### 3. Test Preflight Request

```bash
curl -X OPTIONS http://localhost:5555/api/stocks \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v
```

Expected response should include:
- `Access-Control-Allow-Origin: http://localhost:5173`
- `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`
- `Access-Control-Allow-Credentials: true`

### 4. Verify Security Headers

```bash
curl -I http://localhost:5555/health
```

Expected headers:
```
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: ...
```

## Troubleshooting

### Problem: "No 'Access-Control-Allow-Origin' header"

**Cause:** Origin not in allowed list

**Solution:**
1. Check your `.env` file has `ALLOWED_ORIGINS` set
2. Ensure origin exactly matches (including protocol and port)
3. Restart the Flask server after changing `.env`

### Problem: "CORS not configured - no origins allowed"

**Cause:** Production mode without `ALLOWED_ORIGINS` set

**Solution:**
1. Set `ALLOWED_ORIGINS` in `.env`
2. Or set `FLASK_ENV=development` for testing

### Problem: "CORS error only in production"

**Cause:** Using HTTP origin with HTTPS site

**Solution:**
- Use HTTPS origins: `https://yourdomain.com`
- Ensure your frontend uses HTTPS in production

### Problem: Credentials not being sent

**Cause:** Frontend not configured for credentials

**Solution:**
```javascript
// Frontend: Enable credentials in fetch/axios
fetch(url, { credentials: 'include' });

// or with axios
axios.defaults.withCredentials = true;
```

## Migration from Old Configuration

If you have the old insecure configuration:

```python
# OLD (insecure)
CORS(app)
```

Update to:

```python
# NEW (secure) - Already done in web/app.py
# Just configure .env file as shown above
```

## Related Security Issues

This fix addresses:
- **CRITICAL-003:** Overly Permissive CORS Configuration
- Complements **HIGH-006:** CSRF Protection (implemented separately)

## References

- [OWASP CORS Security Guide](https://owasp.org/www-community/attacks/CORS_RequestPreflighScrutiny)
- [MDN: CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [Flask-CORS Documentation](https://flask-cors.readthedocs.io/)

## Version History

- **2026-02-09:** Initial implementation (CRITICAL-003 fix)
  - Environment-based configuration
  - Explicit origin allowlists
  - Security headers added
  - Production defaults to no origins
