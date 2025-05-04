from fastapi import APIRouter
from app.views import URLViews

# Initialize the router
router = APIRouter()

# Create an instance of URLViews
url_views = URLViews()

# Define URL patterns
router.add_api_route(
    "/expand", url_views.expand_url_view, methods=["POST"], name="expand"
)
