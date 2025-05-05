from fastapi import Request
from pydantic import BaseModel
from app.expand import LinkExpander
from app.pwScrapper import PWScrapper
from app.database import SessionLocal
from app.models import URLExpansionLog
import uuid

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
                print('url:', url)
                response = await self.link_expander.handle_url({"url": url})
                print('after handle_url: call')
                print('response:', response)
                if response is None:
                    toReturn["expanded"] = False
                    toReturn["error_message"] = "Error in LinkExpander"
                elif response["expanded"] is False:
                    toReturn["expanded"] = False
                    toReturn["error_message"] = response["error_message"]
                else:
                    toReturn["expanded_url"] = response["expanded_url"]
            except Exception as e:
                toReturn["expanded"] = False
                toReturn["error_message"] = str(e)
                print(f"Error in handle_url: {e}")

            # Save in DB if expansion failed
            if toReturn["expanded"] is False:
                db = SessionLocal()
                try:
                    db.add(URLExpansionLog(
                        url=url,
                        expanded_url=None,
                        expanded=False,
                        error_message=toReturn["error_message"],
                    ))
                    db.commit()
                finally:
                    db.close()
            print('till here it is working', toReturn)
            # Check if the URL matches specific Flipkart patterns
            if (
                "flipkart.com/s/" in toReturn["expanded_url"]
                or "fkrt.it" in toReturn["expanded_url"]
                or "fkrt.cc" in toReturn["expanded_url"]
                or "fkrt.to" in toReturn["expanded_url"]
                or "fkrt.co" in toReturn["expanded_url"]
                or not toReturn["expanded"]
            ):
                print('inside iff for pwscrapper')
                try:
                    print('before pwscrapper expand_urls_sync: call')
                    responseOfPWScrapper = await pwscrapper.expand_urls_sync([url])
                    print('after pwscrapper expand_urls_sync: call')
                    print('responseOfPWScrapper:', responseOfPWScrapper)
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

            # Save in DB after processing Flipkart URLs
            db = SessionLocal()
            try:
                db.add(URLExpansionLog(
                    url=url,
                    expanded_url=toReturn["expanded_url"],
                    expanded=toReturn["expanded"],
                    error_message=toReturn["error_message"],
                ))
                db.commit()
            finally:
                db.close()

            return toReturn, 200
        except Exception as e:
            toReturn["expanded"] = False
            toReturn["error_message"] = str(e)
            return toReturn, 500
