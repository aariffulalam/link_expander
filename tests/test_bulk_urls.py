import argparse
import asyncio
from app.expand import LinkExpander

async def test_bulk_urls(urls):
    """
    Test the expansion of multiple URLs passed via command line using the handle_url method.
    :param urls: List of URLs to expand.
    """
    expander = LinkExpander()  # Initialize the LinkExpander class
    results = []
    for url in urls:
        try:
            # Call the handle_url method with the required dictionary format
            expanded_url = await expander.handle_url({"url": url})
            results.append((url, expanded_url))
        except Exception as e:
            results.append((url, f"Error: {str(e)}"))

    # Print results
    for original, expanded in results:
        print(f"Original: {original}, Expanded: {expanded}")

# if __name__ == "__main__":
#     # Parse command-line arguments
#     parser = argparse.ArgumentParser(
#         description="Test bulk URL expansion using the handle_url method.",
#         epilog="Example usage:\n"
#                "  python test_bulk_urls.py https://bit.ly/3example1 https://tinyurl.com/example2\n"
#                "  python test_bulk_urls.py https://goo.gl/example3 https://invalid-url",
#         formatter_class=argparse.RawTextHelpFormatter  # Allows multiline examples in the help text
#     )
#     parser.add_argument(
#         "urls",
#         metavar="URL",
#         type=str,
#         nargs="+",
#         help="List of URLs to test (space-separated).",
#     )
#     args = parser.parse_args()

#     # Run the test with the provided URLs
#     asyncio.run(test_bulk_urls(args.urls))