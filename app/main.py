from fastapi import FastAPI
from app.database import engine, Base
from app.routers import clinic, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MedSync API",
    description="Sistema de agendamentos de consultas médicas."
)

app.include_router(auth.router)
app.include_router(clinic.router)

@app.get("/")
def root():
    return {"mensagem": "MedSync API rodando perfeitamente."}