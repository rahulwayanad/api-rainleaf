from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, contacts, bookings, villas, availability, expenses

app = FastAPI(
    title="Rainleaf Family Retreat API",
    description="Backend API for Rainleaf Family Retreat — Wayanad, Kerala",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://rainleafresort.com",
        "https://www.rainleafresort.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(contacts.router)
app.include_router(bookings.router)
app.include_router(villas.router)
app.include_router(availability.router)
app.include_router(expenses.router)


@app.get("/")
def root():
    return {"message": "Rainleaf Family Retreat API is running"}
