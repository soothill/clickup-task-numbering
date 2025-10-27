# ClickUp Epic and Task Numbering Script

This script automatically numbers your ClickUp epics and tasks with a clean, hierarchical numbering system.

## Numbering Scheme

- **Epics**: Numbered in increments of 10 (10, 20, 30, 40, etc.)
- **Tasks**: Numbered with decimal sub-numbers under their parent epic (10.1, 10.2, 10.3, etc.)

### Example Output

```
10. Design Phase
  10.1. Create wireframes
  10.2. Design mockups
  10.3. User testing

20. Development Phase
  20.1. Set up development environment
  20.2. Build frontend
  20.3. Build backend

30. Testing Phase
  30.1. Write unit tests
  30.2. Integration testing
```

## Prerequisites

1. **Python 3.6+** installed on your system
2. **ClickUp API Token** - Get yours from: https://app.clickup.com/settings/apps
3. **List ID** - The ID of the ClickUp list you want to number

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Or install requests directly:

```bash
pip install requests
```

## Getting Your ClickUp List ID

1. Open ClickUp and navigate to the list you want to number
2. Look at the URL in your browser. It will look like:
   ```
   https://app.clickup.com/WORKSPACE_ID/v/li/LIST_ID
   ```
3. Copy the `LIST_ID` from the URL

## Usage

### Dry Run (Recommended First Step)

Before making any changes, do a dry run to see what will be changed:

```bash
python clickup_numbering.py \
  --api-token "pk_YOUR_API_TOKEN" \
  --list-id "YOUR_LIST_ID" \
  --dry-run
```

### Apply Changes

Once you're happy with the preview, run without the `--dry-run` flag:

```bash
python clickup_numbering.py \
  --api-token "pk_YOUR_API_TOKEN" \
  --list-id "YOUR_LIST_ID"
```

## Command Line Arguments

- `--api-token` (required): Your ClickUp API token
- `--list-id` (required): The ID of the ClickUp list to process
- `--dry-run` (optional): Preview changes without applying them

## How It Works

1. **Fetches all tasks** from the specified ClickUp list
2. **Identifies epics** (tasks with no parent task)
3. **Sorts epics** by their position in the list
4. **Finds subtasks** for each epic and sorts them by position
5. **Numbers epics** starting at 10, incrementing by 10 (10, 20, 30...)
6. **Numbers subtasks** with decimal notation (10.1, 10.2, 10.3...)
7. **Removes existing numbering** before applying new numbers to avoid duplication

## Important Notes

- The script only processes **open tasks** (closed tasks are ignored)
- Tasks are numbered based on their current **order/position** in ClickUp
- If a task already has a number prefix, it will be **removed and replaced**
- The script identifies epics as **tasks with no parent**
- Make sure to use `--dry-run` first to preview changes!

## Example with Environment Variables

For better security, you can use environment variables:

```bash
export CLICKUP_API_TOKEN="pk_YOUR_API_TOKEN"
export CLICKUP_LIST_ID="YOUR_LIST_ID"

python clickup_numbering.py \
  --api-token "$CLICKUP_API_TOKEN" \
  --list-id "$CLICKUP_LIST_ID" \
  --dry-run
```

## Troubleshooting

### Authentication Error

If you get an authentication error:
- Verify your API token is correct
- Make sure the token has access to the workspace and list
- Check that you included the full token (starts with `pk_`)

### List Not Found

If you get a "list not found" error:
- Double-check the List ID from the URL
- Ensure you have access to the list
- Verify the list isn't in a private space you don't have access to

### Tasks Not Updating

If tasks aren't being numbered:
- Check that you're not using `--dry-run` flag
- Verify you have edit permissions for the list
- Ensure the tasks aren't closed (script only processes open tasks)

## API Rate Limits

ClickUp has API rate limits. For large lists:
- The script processes tasks sequentially to avoid hitting rate limits
- If you encounter rate limit errors, wait a few minutes and try again

## Support

For ClickUp API documentation, visit: https://clickup.com/api

## License

This script is provided as-is for personal and commercial use.
