#!/usr/bin/env python3
"""
ClickUp Epic and Task Numbering Script

This script connects to ClickUp and numbers epics and tasks using a custom field:
- Epics are numbered in increments of 10 (10, 20, 30, etc.)
- Tasks under each epic are numbered with decimal sub-numbers (10.1, 10.2, etc.)
- By default, updates the "PM.Prio" custom field (configurable via --field-name)
"""

import requests
import json
from typing import List, Dict, Optional
import sys


class ClickUpNumbering:
    def __init__(self, api_token: str):
        """
        Initialize the ClickUp API client.
        
        Args:
            api_token: Your ClickUp API token
        """
        self.api_token = api_token
        self.base_url = "https://api.clickup.com/api/v2"
        self.headers = {
            "Authorization": api_token,
            "Content-Type": "application/json"
        }
    
    def get_list_tasks(self, list_id: str, include_subtasks: bool = True) -> List[Dict]:
        """
        Fetch all tasks from a ClickUp list.

        Args:
            list_id: The ID of the ClickUp list
            include_subtasks: Whether to include subtasks

        Returns:
            List of task dictionaries
        """
        url = f"{self.base_url}/list/{list_id}/task"
        params = {
            "subtasks": str(include_subtasks).lower(),
            "include_closed": "false",
            "include_custom_fields": "true"
        }

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        return response.json().get("tasks", [])
    
    def get_custom_field_id(self, task: Dict, field_name: str) -> Optional[str]:
        """
        Get the field ID for a custom field by name.

        Args:
            task: The task dictionary containing custom fields
            field_name: The name of the custom field to find

        Returns:
            The field ID if found, None otherwise
        """
        custom_fields = task.get("custom_fields", [])
        for field in custom_fields:
            if field.get("name") == field_name:
                return field.get("id")
        return None

    def get_custom_field_info(self, task: Dict, field_name: str) -> Optional[Dict]:
        """
        Get the full custom field info by name.

        Args:
            task: The task dictionary containing custom fields
            field_name: The name of the custom field to find

        Returns:
            The field dictionary if found, None otherwise
        """
        custom_fields = task.get("custom_fields", [])
        for field in custom_fields:
            if field.get("name") == field_name:
                return field
        return None

    def update_custom_field(self, task_id: str, field_id: str, value: str, field_type: str = None, type_config: dict = None) -> bool:
        """
        Update a task's custom field value.

        Args:
            task_id: The ID of the task
            field_id: The ID of the custom field
            value: The new value for the custom field
            field_type: The type of the custom field (optional, for proper formatting)
            type_config: The type configuration (for dropdown/select fields)

        Returns:
            True if successful, False otherwise
        """
        url = f"{self.base_url}/task/{task_id}/field/{field_id}"

        # Check if this is a dropdown/select field with predefined options
        if type_config and 'options' in type_config and len(type_config['options']) > 0:
            # This is a dropdown field - we cannot use arbitrary text values
            raise ValueError(
                f"Field type '{field_type}' has predefined options and cannot accept arbitrary values. "
                f"Please either:\n"
                f"  1. Change the field to a plain text field (remove options) in ClickUp, OR\n"
                f"  2. Use a different custom field without predefined options"
            )

        # Format value based on field type
        # For number fields, convert to numeric type
        if field_type == "number":
            try:
                # Try to parse as float first, then int if it's a whole number
                numeric_value = float(value)
                if numeric_value.is_integer():
                    numeric_value = int(numeric_value)
                data = {"value": numeric_value}
            except ValueError:
                # If conversion fails, send as string
                data = {"value": value}
        else:
            # For text and other field types, send as string
            data = {"value": value}

        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()

        return response.status_code == 200
    
    def organize_tasks_by_hierarchy(self, tasks: List[Dict]) -> Dict:
        """
        Organize tasks into epics and their subtasks.
        
        Args:
            tasks: List of all tasks from ClickUp
            
        Returns:
            Dictionary with epics and their associated tasks
        """
        # Separate epics (tasks with no parent) and subtasks
        epics = []
        task_map = {task["id"]: task for task in tasks}
        
        for task in tasks:
            # A task is considered an epic if it has no parent
            if not task.get("parent"):
                epics.append(task)
        
        # Sort epics by their order_index
        epics.sort(key=lambda x: x.get("order_index", 0))
        
        # Organize subtasks under their parent epics
        organized = {"epics": []}
        
        for epic in epics:
            epic_data = {
                "task": epic,
                "subtasks": []
            }
            
            # Find all subtasks for this epic
            for task in tasks:
                if task.get("parent") == epic["id"]:
                    epic_data["subtasks"].append(task)
            
            # Sort subtasks by their order_index
            epic_data["subtasks"].sort(key=lambda x: x.get("order_index", 0))
            
            organized["epics"].append(epic_data)
        
        return organized
    
    def get_custom_field_value(self, task: Dict, field_name: str) -> Optional[str]:
        """
        Get the current value of a custom field.

        Args:
            task: The task dictionary containing custom fields
            field_name: The name of the custom field

        Returns:
            The field value if found, None otherwise
        """
        custom_fields = task.get("custom_fields", [])
        for field in custom_fields:
            if field.get("name") == field_name:
                return field.get("value")
        return None
    
    def number_tasks(self, list_id: str, dry_run: bool = False, field_name: str = "PM.Prio") -> None:
        """
        Number all epics and tasks in a ClickUp list using a custom field.

        Args:
            list_id: The ID of the ClickUp list
            dry_run: If True, only show what would be changed without making changes
            field_name: Name of the custom field to update (default: "PM.Prio")
        """
        print(f"Fetching tasks from list {list_id}...")
        tasks = self.get_list_tasks(list_id)

        if not tasks:
            print("No tasks found in this list.")
            return

        print(f"Found {len(tasks)} tasks. Organizing by hierarchy...")
        organized = self.organize_tasks_by_hierarchy(tasks)

        print(f"\nFound {len(organized['epics'])} epics.\n")

        # Number the epics and their subtasks
        epic_number = 10

        for epic_data in organized["epics"]:
            epic = epic_data["task"]
            subtasks = epic_data["subtasks"]

            # Get the custom field info for this epic
            field_info = self.get_custom_field_info(epic, field_name)
            if not field_info:
                print(f"⚠ Warning: Custom field '{field_name}' not found on epic '{epic['name']}'")
                print(f"  Skipping epic and its subtasks\n")
                epic_number += 10
                continue

            field_id = field_info.get("id")
            field_type = field_info.get("type")
            type_config = field_info.get("type_config", {})

            # Get current and new values for the epic
            current_value = self.get_custom_field_value(epic, field_name)
            new_value = str(epic_number)

            print(f"Epic {epic_number}: {epic['name']}")
            print(f"  Current {field_name}: {current_value if current_value else '(empty)'}")
            print(f"  New {field_name}: {new_value}")
            print(f"  Field type: {field_type}")

            if not dry_run:
                try:
                    self.update_custom_field(epic["id"], field_id, new_value, field_type, type_config)
                    print(f"  ✓ Updated")
                except Exception as e:
                    print(f"  ✗ Error: {str(e)}")
            else:
                print(f"  (Dry run - no changes made)")

            # Number the subtasks
            for idx, subtask in enumerate(subtasks, start=1):
                # Get the custom field info for this subtask
                subtask_field_info = self.get_custom_field_info(subtask, field_name)
                if not subtask_field_info:
                    print(f"  ⚠ Warning: Custom field '{field_name}' not found on task '{subtask['name']}'")
                    print(f"    Skipping task")
                    continue

                subtask_field_id = subtask_field_info.get("id")
                subtask_field_type = subtask_field_info.get("type")
                subtask_type_config = subtask_field_info.get("type_config", {})

                current_subtask_value = self.get_custom_field_value(subtask, field_name)
                new_subtask_value = f"{epic_number}.{idx}"

                print(f"  Task {epic_number}.{idx}: {subtask['name']}")
                print(f"    Current {field_name}: {current_subtask_value if current_subtask_value else '(empty)'}")
                print(f"    New {field_name}: {new_subtask_value}")
                print(f"    Field type: {subtask_field_type}")

                if not dry_run:
                    try:
                        self.update_custom_field(subtask["id"], subtask_field_id, new_subtask_value, subtask_field_type, subtask_type_config)
                        print(f"    ✓ Updated")
                    except Exception as e:
                        print(f"    ✗ Error: {str(e)}")
                else:
                    print(f"    (Dry run - no changes made)")

            print()  # Empty line between epics
            epic_number += 10

        if dry_run:
            print("\n" + "="*60)
            print("DRY RUN COMPLETE - No changes were made")
            print("Run without --dry-run flag to apply changes")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("NUMBERING COMPLETE")
            print("="*60)


def main():
    """Main function to run the script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Number ClickUp epics and tasks with incremental numbering using custom fields"
    )
    parser.add_argument(
        "--api-token",
        required=True,
        help="Your ClickUp API token"
    )
    parser.add_argument(
        "--list-id",
        required=True,
        help="The ClickUp list ID to process"
    )
    parser.add_argument(
        "--field-name",
        default="PM.Prio",
        help="Custom field name to update (default: PM.Prio)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them"
    )

    args = parser.parse_args()

    try:
        numbering = ClickUpNumbering(args.api_token)
        numbering.number_tasks(args.list_id, dry_run=args.dry_run, field_name=args.field_name)
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with ClickUp API: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
