import csv
import time
from pathlib import Path
import httpx
import pytest

# Define the base URL for the FastAPI app
BASE_URL = "http://localhost:8000"

# Define the input and output CSV file paths
INPUT_CSV = Path("/app/tests/input_urls.csv")
OUTPUT_CSV = Path("/app/tests/output_results.csv")


@pytest.mark.asyncio
async def test_expand_endpoint() -> None:
    """Test the /expand endpoint with URLs from a CSV file."""
    # Ensure the output directory exists
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    # Open the input CSV and read URLs and expected results
    with INPUT_CSV.open("r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        test_cases = [
            {"url": row["url"], "expected": row["expected"] if "expected" in row else None}
            for row in reader
        ]

    # Prepare the output CSV
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as outfile:
        fieldnames = ["url", "expected", "status_code", "response_time", "result", "pass"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        # Send POST requests to /expand
        async with httpx.AsyncClient() as client:
            pass_count = 0
            for case in test_cases:
                start_time = time.time()
                response = await client.post(f"{BASE_URL}/expand", json={"url": case["url"]})
                end_time = time.time()

                # Determine if the test passed
                test_passed = False
                actual_result = None
                if response.status_code == 200:
                    actual_result = response.json()
                    test_passed = (
                        actual_result["expanded_url"] == case["expected"]
                        if case["expected"]
                        else False
                    )
                    if test_passed:
                        pass_count += 1

                # Write the result to the output CSV
                writer.writerow(
                    {
                        "url": case["url"],
                        "expected": case["expected"] if case["expected"] else None,
                        "status_code": response.status_code,
                        "response_time": end_time - start_time,
                        "result": (actual_result["expanded_url"] if actual_result else ""),
                        "pass": test_passed,
                    }
                )

            # Calculate and log the pass percentage
            total_tests = len(test_cases)
            pass_percentage = (pass_count / total_tests) * 100 if total_tests > 0 else 0
            assert pass_percentage == 100, f"Pass percentage: {pass_percentage:.2f}%"
