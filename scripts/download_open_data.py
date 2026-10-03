"""
Download the Open Data Pakistan Zameen Property Data CSV.

The publisher page states that the resource is CC Attribution.
Run this on a machine with internet access.

Usage:
    python scripts/download_open_data.py
"""
from pathlib import Path
import urllib.request

URL = "https://opendata.com.pk/dataset/9e959916-1cfc-4e28-85c8-f10ff63e5df2/resource/2cb1eeea-8dff-41b4-845f-28b8d75ca23b/download/zameen-property-data.csv"
OUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "zameen_property_data.csv"

OUT.parent.mkdir(parents=True, exist_ok=True)
print("Downloading Open Data Pakistan resource...")
urllib.request.urlretrieve(URL, OUT)
print(f"Saved {OUT}")
