#!/usr/bin/env python3
"""
Test script to manually update a custom field
"""

import os
import sys
import requests
import json

# Set your API key here or via environment variable
API_KEY = os.environ.get("CLICKUP_API_KEY", "")
TASK_ID = "869axze2m"  # Epic 4 from your output
FIELD_ID = "0940823b-562b-44d3-90a7-2bb82b4cacbe"  # PM.Prio field

if not API_KEY:
    print("Please set CLICKUP_API_KEY environment variable")
    sys.exit(1)

# Test different payload formats
test_cases = [
    {"value": "10"},
    {"value": 10},
    {"value": {"text": "10"}},
]

base_url = "https://api.clickup.com/api/v2"
headers = {
    "Authorization": API_KEY,
    "Content-Type": "application/json"
}

for i, data in enumerate(test_cases, 1):
    print(f"\nTest {i}: {json.dumps(data)}")
    url = f"{base_url}/task/{TASK_ID}/field/{FIELD_ID}"

    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            print("✓ SUCCESS!")
            break
    except Exception as e:
        print(f"Error: {e}")
