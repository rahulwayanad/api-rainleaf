from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from routers import auth, contacts, bookings

# Create all tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Rainleaf Family Retreat API",
    description="Backend API for Rainleaf Family Retreat — Wayanad, Kerala",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://www.rainleafresort.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(contacts.router)
app.include_router(bookings.router)


@app.get("/")
def root():
    return {"message": "Rainleaf Family Retreat API is running"}
