import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.models import EmailRequest, EmailResponse
from app.email_service import email_service

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Mailbridge")
    logger.info(f"Configured recipient: {settings.recipient_email}")
    logger.info(f"SMTP server: {settings.smtp_host}:{settings.smtp_port}")
    yield
    logger.info("Shutting down Mailbridge")


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Simple, production-ready email notification service",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=dict)
async def root():
    return {
        "service": settings.api_title,
        "version": settings.api_version,
        "status": "healthy"
    }


@app.get("/health", response_model=dict)
async def health_check():
    return {
        "status": "healthy",
        "smtp_configured": bool(settings.smtp_username and settings.smtp_password),
        "recipient_configured": bool(settings.recipient_email)
    }


@app.post("/send-email", response_model=EmailResponse, status_code=status.HTTP_200_OK)
async def send_email(email_request: EmailRequest):
    try:
        logger.info(f"Processing email request from {email_request.email}")
        await email_service.send_notification_email(email_request)
        return EmailResponse(success=True, message="Email sent successfully")
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}"
        )


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"success": False, "message": str(exc)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "message": "Internal server error"}
    )
