import os
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "tinyllama")
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "BACKEND_CORS_ORIGINS", "http://localhost,http://127.0.0.1"
    ).split(",")
    if origin.strip()
]

app = FastAPI(
    title="Ollama Chat Backend",
    description="Backend FastAPI que actua como puente entre el frontend y Ollama.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Prompt del usuario")


class ChatResponse(BaseModel):
    model: str
    response: str


def health_payload() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "backend",
        "ollama_url": OLLAMA_URL,
        "ollama_model": OLLAMA_MODEL,
    }


@app.get("/health")
@app.get("/api/health")
async def health() -> dict[str, str]:
    return health_payload()


async def call_ollama(prompt: str) -> dict[str, Any]:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
    except httpx.ConnectError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "No se pudo conectar con Ollama. Comprueba que el contenedor este "
                "levantado y accesible en la red interna."
            ),
        ) from exc
    except httpx.ReadTimeout as exc:
        raise HTTPException(
            status_code=504,
            detail="Ollama ha tardado demasiado en responder.",
        ) from exc

    if response.status_code >= 400:
        details = response.text.strip() or "Respuesta de error sin detalle."
        if "model" in details.lower() and "not found" in details.lower():
            raise HTTPException(
                status_code=503,
                detail=(
                    f"El modelo '{OLLAMA_MODEL}' no esta descargado en Ollama. "
                    "Ejecuta el script scripts/pull-model.sh para cargarlo."
                ),
            )

        raise HTTPException(
            status_code=502,
            detail=f"Ollama devolvio un error: {details}",
        )

    return response.json()


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    result = await call_ollama(request.prompt.strip())
    model = str(result.get("model", OLLAMA_MODEL))
    generated_text = str(result.get("response", "")).strip()

    if not generated_text:
        raise HTTPException(
            status_code=502,
            detail="Ollama respondio, pero no devolvio contenido de texto.",
        )

    return ChatResponse(model=model, response=generated_text)
