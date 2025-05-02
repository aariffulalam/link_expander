# Link Expander

Link Expander is a FastAPI-based application that processes URLs, expands shortened links, and handles specific URL patterns like `linkredirect.in` and `hypd.store`.

## Features

- Expands shortened URLs by following redirects.
- Handles specific URL patterns:
  - Extracts the `dl` parameter from `linkredirect.in` URLs.
  - Expands `hypd.store` URLs by calling the Hypd API.
- Validates and fixes malformed URLs (e.g., adds `https://` if missing).
- Logs errors and provides detailed feedback for debugging.

## Requirements

- Python 3.8+
- FastAPI
- Requests

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/link-expander.git
   cd link-expander