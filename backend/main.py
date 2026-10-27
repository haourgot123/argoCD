import os
import socket

from fastapi import FastAPI

APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_ENV = os.getenv("APP_ENV", "local")
APP_MESSAGE = os.getenv("APP_MESSAGE", "Hello from FastAPI!")

app = FastAPI(title="ArgoCD Lab API", version=APP_VERSION)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": APP_MESSAGE, "version": APP_VERSION}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/info")
async def info() -> dict[str, str]:
    return {
        "app": "argocd-lab-api",
        "version": APP_VERSION,
        "environment": APP_ENV,
        "hostname": socket.gethostname(),
    }
