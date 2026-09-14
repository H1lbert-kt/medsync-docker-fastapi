from fastapi import FastAPI
from app.routers import clinic, auth

app = FastAPI(
    title="MedSync API",
    description="Sistema de agendamentos de consultas médicas."
)

app.include_router(auth.router)
app.include_router(clinic.router)

@app.get("/")
def root():
    return {"mensagem": "MedSync API rodando perfeitamente."}