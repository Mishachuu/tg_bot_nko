from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import equipment_photos
# from app.api.routers import equipment, bookings, users, categories
from app.api.routers import users
from app.api.routers import equipment

app = FastAPI(
    title="NKO Bot API",
    description="API for equipment rental bot",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(equipment.router)
# app.include_router(bookings.router)
app.include_router(users.router)
# app.include_router(categories.router)
app.include_router(equipment_photos.router)


@app.get("/")
async def root():
    return {"message": "NKO Bot API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}