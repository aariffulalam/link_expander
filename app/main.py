from fastapi import FastAPI, Request
from pydantic import BaseModel
from app.expand import handle_url
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class URLRequest(BaseModel):
    url: str

@app.post("/expand")
async def expand_link(request: URLRequest):
    print(f"expand_link function Received URL:")
    try:
        logger.info(f"expand_link function Received URL: {request.url}")
        expanded = await handle_url(request.url)
        return {"original": request.url, "expanded": expanded}
    except Exception as e:
        logger.error(f"Error in expand_link function: {e}")
        return {"error": "An error occurred while processing the URL"}
