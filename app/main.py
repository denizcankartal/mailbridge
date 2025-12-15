import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import ContactRequestCreate, ContactRequestResponse
from app.database import get_db, init_db
from app.db_models import ContactRequest

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting ContactStore")
    logger.info(f"Database: {settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down ContactStore")


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Simple, production-ready contact request storage service",
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
        "database_configured": bool(settings.postgres_user and settings.postgres_password)
    }


@app.post("/submit-request", response_model=ContactRequestResponse, status_code=status.HTTP_201_CREATED)
async def submit_request(
    request: ContactRequestCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        logger.info(f"Processing contact request from {request.email}")

        contact_request = ContactRequest(
            fullname=request.fullname,
            email=str(request.email),
            phone=request.phone,
            company=request.company,
            message=request.message
        )

        db.add(contact_request)
        await db.commit()
        await db.refresh(contact_request)

        logger.info(f"Contact request saved with ID {contact_request.id} from {request.email}")
        return ContactRequestResponse(success=True, message="Request submitted successfully")

    except Exception as e:
        logger.error(f"Failed to save contact request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit request: {str(e)}"
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
