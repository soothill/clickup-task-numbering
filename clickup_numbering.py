#!/usr/bin/env python3
"""
ClickUp Epic and Task Numbering Script

This script connects to ClickUp and numbers epics and tasks:
- Epics are numbered in increments of 10 (10, 20, 30, etc.)
- Tasks under each epic are numbered with decimal sub-numbers (10.1, 10.2, etc.)
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
            "include_closed": "false"
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        return response.json().get("tasks", [])
    
    def update_task_name(self, task_id: str, new_name: str) -> bool:
        """
        Update a task's name.
        
        Args:
            task_id: The ID of the task
            new_name: The new name for the task
            
        Returns:
            True if successful, False otherwise
        """
        url = f"{self.base_url}/task/{task_id}"
        data = {"name": new_name}
        
        response = requests.put(url, headers=self.headers, json=data)
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
    
    def strip_existing_number(self, task_name: str) -> str:
        """
        Remove existing numbering from task name if present.
        
        Args:
            task_name: The task name that may contain numbering
            
        Returns:
            Task name without numbering prefix
        """
        parts = task_name.split(" ", 1)
        if len(parts) > 1:
            # Check if first part looks like a number (e.g., "10", "10.1", "20.3")
            first_part = parts[0].rstrip(".")
            if first_part.replace(".", "").isdigit():
                return parts[1]
        return task_name
    
    def number_tasks(self, list_id: str, dry_run: bool = False) -> None:
        """
        Number all epics and tasks in a ClickUp list.
        
        Args:
            list_id: The ID of the ClickUp list
            dry_run: If True, only show what would be changed without making changes
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
            
            # Clean and number the epic
            clean_epic_name = self.strip_existing_number(epic["name"])
            new_epic_name = f"{epic_number}. {clean_epic_name}"
            
            print(f"Epic {epic_number}: {clean_epic_name}")
            print(f"  Old: {epic['name']}")
            print(f"  New: {new_epic_name}")
            
            if not dry_run:
                try:
                    self.update_task_name(epic["id"], new_epic_name)
                    print(f"  ✓ Updated")
                except Exception as e:
                    print(f"  ✗ Error: {str(e)}")
            else:
                print(f"  (Dry run - no changes made)")
            
            # Number the subtasks
            for idx, subtask in enumerate(subtasks, start=1):
                clean_subtask_name = self.strip_existing_number(subtask["name"])
                new_subtask_name = f"{epic_number}.{idx}. {clean_subtask_name}"
                
                print(f"  Task {epic_number}.{idx}: {clean_subtask_name}")
                print(f"    Old: {subtask['name']}")
                print(f"    New: {new_subtask_name}")
                
                if not dry_run:
                    try:
                        self.update_task_name(subtask["id"], new_subtask_name)
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
        description="Number ClickUp epics and tasks with incremental numbering"
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
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them"
    )
    
    args = parser.parse_args()
    
    try:
        numbering = ClickUpNumbering(args.api_token)
        numbering.number_tasks(args.list_id, dry_run=args.dry_run)
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with ClickUp API: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
