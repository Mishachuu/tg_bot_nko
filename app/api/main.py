from fastapi import FastAPI
# from app.api.routers import equipment, bookings, users, categories
from app.api.routers import users

app = FastAPI(
    title="NKO Bot API",
    description="API for equipment rental bot",
    version="1.0.0"
)

# Include routers
# app.include_router(equipment.router)
# app.include_router(bookings.router)
app.include_router(users.router)
# app.include_router(categories.router)


@app.get("/")
async def root():
    return {"message": "NKO Bot API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}