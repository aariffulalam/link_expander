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
        body = await request.json()
        url = body.get("url", "")
        toReturn = {
            "expanded": True,
            "url": url,
            "expanded_url": url,
            "error_message": '',
        }
        try:
            if not url or url == "":
                toReturn["expanded"] = False
                toReturn["error_message"] = "URL is required"
                return toReturn, 400

            # Call the handle_url method in a try-except block
            try:
                print('before handle_url: call')
                response = await self.link_expander.handle_url({"url": url})
                print('after handle_url: call')
                #  check if response is undefined or None
                print('response:', response)
                if response is None:
                    toReturn["expanded"] = False
                    toReturn["error_message"] = "Error in LinkExpander"
                elif response.expanded is False:
                    toReturn["expanded"] = False
                    toReturn["error_message"] = response.error_message
                else:
                    toReturn["expanded_url"] = response.expanded_url
            except Exception as e:
                toReturn["expanded"] = False
                # error message from exception
                toReturn["error_message"] = str(e)
                print(f"Error in handle_url: {e}")

            # if toReturn["expanded"] is False:
            #     save in DB and send mail to admin

            # Check if the URL matches specific Flipkart patterns
            if (
                "flipkart.com/s/" in url
                or "fkrt.it" in url
                or "fkrt.cc" in url
                or "fkrt.to" in url
                or "fkrt.co" in url
            ):
                try:
                    # Use pwScrapper's expand_urls_sync function to expand the URL
                    responseOfPWScrapper = await pwscrapper.expand_urls_sync([url])
                    if responseOfPWScrapper and len(responseOfPWScrapper) > 0:
                        expanded = responseOfPWScrapper[0]
                        toReturn["expanded_url"] = expanded
                    else:
                        expanded = None
                        toReturn["expanded"] = False
                        toReturn["error_message"] = (
                            responseOfPWScrapper.error_message
                            if hasattr(responseOfPWScrapper, 'error_message')
                            else "Error in PWScrapper"
                        )
                except Exception as e:
                    expanded = None
                    toReturn["expanded"] = False
                    toReturn["error_message"] = str(e)
                    print(f"Error in expand_urls_sync: {e}")

            return toReturn, 200
        except Exception as e:
            toReturn["expanded"] = False
            toReturn["error_message"] = str(e)
            return toReturn, 500
