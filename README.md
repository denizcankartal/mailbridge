# Mailbridge

A simple, clean, and production-ready email notification service built with FastAPI. Bridges contact form submissions to your email inbox.

- Simple REST API with single `/send-email` endpoint
- Production-ready Docker image with multi-stage builds
- Input validation and sanitization (prevents injection attacks)
- SMTP support (Gmail and other providers)
- Responsive HTML email templates
- Health check endpoint for monitoring
- CORS enabled for frontend integration
- GitHub Actions CI/CD for automatic Docker image publishing

**Example Use Case**

- User submit a form on a website (name, email, phone, company, message)
- The form data is sent to this API
- The API sends a formatted email to the business email
- The business email receives the template email with all sender details

## Quick Start

### 1. Configure

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
RECIPIENT_EMAIL=your-business@example.com
RECIPIENT_NAME=Your Business Name

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-gmail@gmail.com
SMTP_PASSWORD=your-app-specific-password
SMTP_USE_TLS=true
```

**Gmail SMTP Setup:**
1. Enable 2-Factor Authentication on your Google account
2. Go to [Google Account Security](https://myaccount.google.com/security)
3. Click "App passwords" (appears only after enabling 2FA)
4. Select "Mail" and "Other (Custom name)"
5. Copy the generated 16-character password
6. Use this password in `SMTP_PASSWORD` (not your regular Gmail password)

### 2. Run with Docker Compose

```bash
docker-compose up -d
```

Service available at `http://localhost:8000`

### 3. Test the API

```bash
curl -X POST http://localhost:8000/send-email \
  -H "Content-Type: application/json" \
  -d '{
    "fullname": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "company": "Acme Corp",
    "message": "I would like to request a demo."
  }'
```

## API Reference

### POST /send-email

Send a contact form notification.

**Request Body:**
```json
{
  "fullname": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "company": "Acme Corp",
  "message": "Optional message"
}
```

**Field Requirements:**
- `fullname`: Required, 1-100 characters
- `email`: Required, valid email format
- `phone`: Required, 1-50 characters
- `company`: Required, 1-200 characters
- `message`: Optional, max 5000 characters

**Success Response (200):**
```json
{
  "success": true,
  "message": "Email sent successfully"
}
```

**Error Response (400/500):**
```json
{
  "success": false,
  "message": "Error description"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "smtp_configured": true,
  "recipient_configured": true
}
```

**Interactive API Docs:** Once running, visit `http://localhost:8000/docs`

## Deployment

**Authentication & Security:**
Mailbridge is designed to run behind an API gateway (Traefik) where authentication and rate limiting are handled. This follows microservices best practices and keeps Mailbridge simple and stateless.

**Traefik Middleware Options:**
- API key authentication
- IP whitelisting
- Rate limiting (example above)
- OAuth/JWT if needed

**Security Features**

- Email format validation using `email-validator`
- String length limits on all fields
- Newline/null byte removal (prevents header injection)
- HTML auto-escaping in templates (prevents XSS)
- Non-root user in Docker container
- Input sanitization on all text fields

**Configuration**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `RECIPIENT_EMAIL` | Yes | - | Email that receives notifications |
| `RECIPIENT_NAME` | Yes | - | Recipient name |
| `SMTP_HOST` | No | `smtp.gmail.com` | SMTP server |
| `SMTP_PORT` | No | `587` | SMTP port |
| `SMTP_USERNAME` | Yes | - | SMTP username |
| `SMTP_PASSWORD` | Yes | - | SMTP password or app-specific password |
| `SMTP_USE_TLS` | No | `true` | Use TLS |
| `API_TITLE` | No | `Mailbridge` | API title |
| `API_VERSION` | No | `1.0.0` | API version |
| `CORS_ORIGINS` | No | `*` | Allowed CORS origins |

## Troubleshooting

### Gmail Authentication Errors

**Error:** "Username and Password not accepted"

**Solution:**
1. Verify 2FA is enabled on your Google account
2. Generate a new App-Specific Password (not your regular password)
3. Make sure you copied the full 16-character password without spaces
4. Update `SMTP_PASSWORD` in your `.env` file

### Email Not Received

**Checklist:**
- Check spam/junk folder in your recipient email
- Verify logs: `docker-compose logs -f mailbridge`
- Test health endpoint: `curl http://localhost:8000/health`
- Confirm SMTP credentials are correct in `.env`
- Ensure SMTP port 587 is not blocked by your firewall

### Connection Timeout

If you get SMTP connection timeouts:
- Try port 465 with `SMTP_PORT=465`
- Check if your network/ISP blocks outbound SMTP
- Verify Gmail allows "Less secure app access" or use app password

## Frontend Integration

```javascript
async function handleContactForm(formData) {
  const response = await fetch('http://localhost:8000/send-email', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      fullname: formData.name,
      email: formData.email,
      phone: formData.phone,
      company: formData.company,
      message: formData.message,
    }),
  });

  const result = await response.json();
  if (result.success) {
    alert('Message sent successfully!');
  } else {
    alert('Failed to send: ' + result.message);
  }
}
```
