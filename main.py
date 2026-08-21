import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from logging_config import configure_logging, logger
from routers import items, projects, tags, tasks, users

configure_logging()

app = FastAPI()


@app.middleware("http")
async def log_unhandled_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:
        logger.exception(
            "Unhandled exception while processing %s %s",
            request.method,
            request.url.path,
        )
        return JSONResponse(
            status_code=500, content={"detail": "Internal Server Error"}
        )


cors_origins = os.getenv(
    "CORS_ORIGINS", "http://localhost:3000,http://localhost:5173"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(tags.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Hello World"}
