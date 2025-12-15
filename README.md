# ContactStore

Contact request storage service built with FastAPI. Stores contact form submissions in PostgreSQL.

## Features

- Simple REST API with `/submit-request` endpoint
- PostgreSQL database for persistent storage
- Input validation and sanitization (prevents injection attacks)
- Health check endpoint for monitoring
- CORS enabled for frontend integration
- Docker-based deployment
- GitHub Actions CI/CD for automatic image publishing

## Quick Start

### 1. Configure

```bash
cp .env.example .env
```

Edit `.env`:

```env
POSTGRES_USER=contactstore
POSTGRES_PASSWORD=changeme
POSTGRES_DB=contactstore
```

### 2. Run

```bash
docker compose up -d
```

The service automatically creates the `contact_requests` table on startup.

### 3. Test

```bash
curl -X POST http://localhost:8000/submit-request \
  -H "Content-Type: application/json" \
  -d '{
    "fullname": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "company": "Acme Corp",
    "message": "I would like to request a demo."
  }'
```

## API

### POST /submit-request

**Request:**
```json
{
  "fullname": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "company": "Acme Corp",
  "message": "Optional message"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Request submitted successfully"
}
```

**Field Requirements:**
- `fullname`: 1-100 characters (required)
- `email`: Valid email format (required)
- `phone`: 1-50 characters (required)
- `company`: 1-200 characters (required)
- `message`: Max 500 characters (optional)

### GET /health

```json
{
  "status": "healthy",
  "database_configured": true
}
```

**Docs:** `http://localhost:8000/docs`

## Database Access

### View Submissions

```bash
docker compose exec contactstore_db psql -U contactstore -d contactstore

SELECT id, fullname, email, company, created_at
FROM contact_requests
ORDER BY created_at DESC LIMIT 10;
```

### Export to CSV

```bash
docker compose exec contactstore_db psql -U contactstore -d contactstore \
  -c "\COPY (SELECT * FROM contact_requests ORDER BY created_at DESC) TO STDOUT WITH CSV HEADER" \
  > submissions.csv
```


### Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `POSTGRES_USER` | Yes | - | Database user |
| `POSTGRES_PASSWORD` | Yes | - | Database password |
| `POSTGRES_DB` | Yes | - | Database name |
| `POSTGRES_HOST` | No | `contactstore_db` | Database host |
| `POSTGRES_PORT` | No | `5432` | Database port |
| `API_TITLE` | No | `ContactStore` | API title |
| `API_VERSION` | No | `1.0.0` | API version |
| `CORS_ORIGINS` | No | `*` | Allowed origins (comma-separated or `*`) |

### Security

- Designed to run behind API gateway (Traefik) for auth/rate limiting
- Email format validation
- String length limits on all fields
- Input sanitization (prevents injection attacks)
- SQL injection protection via SQLAlchemy ORM
- Non-root Docker user