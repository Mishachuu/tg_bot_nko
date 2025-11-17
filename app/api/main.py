from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import equipment_photos
from app.api.routers import users
from app.api.routers import equipment
from app.api.routers import statistics

app = FastAPI(
    title="NKO Bot API",
    description="API for equipment rental bot",
    version="1.0.0"
)

# CORS middleware ДОЛЖЕН БЫТЬ ДО включения роутеров
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular dev server
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],  # Явно указываем PATCH
    allow_headers=["*"],
)

# Include routers ПОСЛЕ CORS middleware
app.include_router(statistics.router)
app.include_router(equipment.router)
app.include_router(users.router)
app.include_router(equipment_photos.router)

@app.get("/")
async def root():
    return {"message": "NKO Bot API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}