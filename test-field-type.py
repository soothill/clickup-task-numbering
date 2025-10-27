#!/usr/bin/env python3
"""
Quick test script to check the PM.Prio field type
"""

import os
import sys

# Set your API key here or via environment variable
API_KEY = os.environ.get("CLICKUP_API_KEY", "")
LIST_ID = "901213682287"

if not API_KEY:
    print("Please set CLICKUP_API_KEY environment variable")
    sys.exit(1)

from clickup_numbering import ClickUpNumbering

numbering = ClickUpNumbering(API_KEY)
tasks = numbering.get_list_tasks(LIST_ID)

if tasks:
    task = tasks[0]
    print(f"Task: {task['name']}")
    print(f"\nCustom fields:")
    for field in task.get("custom_fields", []):
        print(f"  Name: {field.get('name')}")
        print(f"  Type: {field.get('type')}")
        print(f"  ID: {field.get('id')}")
        print(f"  Value: {field.get('value')}")
        print(f"  Type Config: {field.get('type_config', {})}")
        print()
