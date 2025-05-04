from fastapi import FastAPI
from app.urls import router  # Import the router from urls.py
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Include the router
app.include_router(router)
