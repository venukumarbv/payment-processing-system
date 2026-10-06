from fastapi import FastAPI
from src.routers.api_router import api_router

app = FastAPI(
    title="Payment Processing API",
    description="Customer Facing API for managing and Analyzing Payment Transactions",
    version="1.0",
)


# We include the api_router which contains all our:
# 1. Authentication routes (/login)
# 2. Transaction routes (/transactions/{id})
# 3. Analytics routes (/merchants/top)
app.include_router(api_router)


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """
    Root endpoint to verify if the API is online.
    """
    return {
        "status": "Online",
        "message": "Payment Processing API is running successfully",
        "docs": "/docs",
    }
