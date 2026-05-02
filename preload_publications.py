#!/usr/bin/env python3
"""Preload all publication metadata from ADS and cache locally."""

import json
import os
import sys
import urllib.parse
import urllib.request

ADS_API_URL = "https://api.adsabs.harvard.edu/v1/search/query"
FIRST_AUTHOR_LIST = "publications-first-author.txt"
OTHER_PUBLICATIONS_LIST = "publications-other.txt"
FIRST_CACHE_FILE = "publications-cache-first-author.json"
OTHER_CACHE_FILE = "publications-cache-other.json"
REQUEST_TIMEOUT = int(os.environ.get("ADS_REQUEST_TIMEOUT", "60"))


def load_bibcodes(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def preload_publications(token, input_file, output_file):
    """Fetch publications for an input list and cache them."""
    bibcodes = load_bibcodes(input_file)
    if not bibcodes:
        print(f"No bibcodes found in {input_file}")
        return

    headers = {"Authorization": f"Bearer {token}"}
    docs = []

    print(f"Fetching {len(bibcodes)} publications from {input_file}...")
    for i, bibcode in enumerate(bibcodes, 1):
        try:
            params = {
                "q": f'bibcode:"{bibcode}"',
                "fl": "title,author,bibcode,year,pub,abstract",
                "rows": 1,
            }
            url = f"{ADS_API_URL}?{urllib.parse.urlencode(params)}"
            request = urllib.request.Request(url, headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            })
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
                body = response.read().decode("utf-8")
                data = json.loads(body)

            if data.get("response", {}).get("docs"):
                docs.append(data["response"]["docs"][0])
                print(f"  [{i}/{len(bibcodes)}] ✓ {bibcode}")
            else:
                print(f"  [{i}/{len(bibcodes)}] ✗ {bibcode} (not found)")
        except Exception as e:
            print(f"  [{i}/{len(bibcodes)}] ✗ {bibcode} ({e})")

    cache_data = {"response": {"docs": docs}}
    with open(output_file, "w") as f:
        json.dump(cache_data, f, indent=2)

    print(f"\n✅ Cached {len(docs)} publications to {output_file}")


def main():
    token = os.environ.get("ADS_API_TOKEN")
    if not token:
        print("ERROR: Set ADS_API_TOKEN in your environment")
        print("  ADS_API_TOKEN=your_token python3 preload_publications.py")
        sys.exit(1)

    if os.path.exists(FIRST_AUTHOR_LIST):
        preload_publications(token, FIRST_AUTHOR_LIST, FIRST_CACHE_FILE)
    else:
        print(f"Warning: {FIRST_AUTHOR_LIST} not found.")

    if os.path.exists(OTHER_PUBLICATIONS_LIST):
        preload_publications(token, OTHER_PUBLICATIONS_LIST, OTHER_CACHE_FILE)
    else:
        print(f"Warning: {OTHER_PUBLICATIONS_LIST} not found.")


if __name__ == "__main__":
    main()
