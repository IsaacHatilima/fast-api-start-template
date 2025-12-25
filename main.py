from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status, APIRouter
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.settings import get_settings
from app.controllers import user_router
from app.database.redis_client import redis_client
from app.database.session import engine, init_db

settings = get_settings()


# -------------------------
# Lifespan (startup/shutdown)
# -------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await init_db(engine)
    try:
        yield
    finally:
        # shutdown (order matters)
        await redis_client.close()
        await engine.dispose()


# -------------------------
# App
# -------------------------
docs_url = "/docs" if settings.APP_ENV == "development" else None
redoc_url = "/redoc" if settings.APP_ENV == "development" else None
openapi_url = "/openapi.json" if settings.APP_ENV == "development" else None

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="FastAPI starter project with PostgreSQL and Redis",
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url=docs_url,
    redoc_url=redoc_url,
    openapi_url=openapi_url,
)


# -------------------------
# Validation error handler
# -------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
):
    errors = {}
    for err in exc.errors():
        field = err["loc"][-1]
        errors[field] = err["msg"]

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"errors": errors},
    )


# -------------------------
# Middleware
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Routers
# -------------------------
api_router = APIRouter(prefix="/api")
api_router.include_router(user_router)
app.include_router(api_router)


# -------------------------
# Routes
# -------------------------
@app.get("/")
async def root():
    return {
        "message": "Welcome to FastAPI Starter",
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.APP_ENV == "development" else None,
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
