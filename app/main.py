# app/main.py
from fastapi import FastAPI
from .routers import call

app = FastAPI(
    title="Articence Voice Bot Microservice",
    description="FastAPI backend for ingesting audio packets and orchestrating AI processing",
    version="0.1.0"
)

app.include_router(call.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}