import pytest
import asyncio
from app.views import URLViews  # Import the URLViews class

# Initialize the URLViews class
url_views = URLViews()

@pytest.mark.asyncio
@pytest.mark.parametrize("url", [
    "https://dl.flipkart.com/s/VaWLGAuuuN",
    "https://fkrt.co/Pt8CUR",
    "https://fkrt.it/wy!CFYNNNN"
])
async def test_url_status(url):
    # Simulate a request body with the URL
    request_body = {"url": url}
    
    # Call the expand_url_view function
    response, status_code = await url_views.expand_url_view(MockRequest(request_body))
    
    # Assert the status code and response
    assert status_code == 200, f"Failed: {url} returned status {status_code}"
    assert response["expanded"], f"Failed: {url} was not expanded successfully"
    print(f"Success: {url} expanded to {response['expanded_url']}")


class MockRequest:
    """
    A mock request class to simulate FastAPI's Request object.
    """
    def __init__(self, json_body):
        self._json = json_body

    async def json(self):
        return self._json