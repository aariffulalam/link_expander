from fastapi import Request
from pydantic import BaseModel
from app.expand import LinkExpander
from app.pwScrapper import PWScrapper  # Import expand_urls_sync from pwScrapper

# Initialize the LinkExpander class
link_expander = LinkExpander()

# Initialize the PWScrapper class
pwscrapper = PWScrapper()


class URLRequest(BaseModel):
    url: str


class URLViews:
    def __init__(self):
        self.link_expander = link_expander

    async def expand_url_view(self, request: Request):
        try:
            body = await request.json()
            url = body.get("url", "")
            expanded = url
            if not url or url == "":
                return {"error": "URLs are required"}, 400

            # Call the handle_url method in a try-except block
            try:
                expanded = await self.link_expander.handle_url({"url": url})
            except Exception as e:
                # Log the exception (optional)
                print(f"Error in handle_url: {e}")
                # Do nothing and proceed to the next block

            # Check if the URL matches specific Flipkart patterns
            if (
                "flipkart.com/s/" in url
                or "fkrt.it" in url
                or "fkrt.cc" in url
                or "fkrt.to" in url
                or "fkrt.co" in url
            ):
                # Use pwScrapper's expand_urls_sync function to expand the URL
                expanded = await pwscrapper.expand_urls_sync([url])

            return {"original": url, "expanded": expanded}
        except Exception as e:
            return {"error": f"An error occurred: {e}"}
