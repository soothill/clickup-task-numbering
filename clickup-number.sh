#!/bin/bash

# ClickUp Task Numbering Wrapper Script
#
# This script runs the ClickUp numbering Python script with support for:
# - Environment variables (CLICKUP_API_KEY, CLICKUP_LIST_ID)
# - Command-line override for list ID
# - Help documentation

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display help
show_help() {
    cat << EOF
${GREEN}ClickUp Task Numbering Script${NC}

Numbers ClickUp epics and tasks with incremental numbering using a custom field:
- Epics are numbered in increments of 10 (10, 20, 30, etc.)
- Tasks under each epic are numbered with decimal sub-numbers (10.1, 10.2, etc.)
- Updates a custom field (default: PM.Prio) rather than task names

${YELLOW}USAGE:${NC}
    $(basename "$0") [OPTIONS] [LIST_ID]

${YELLOW}ENVIRONMENT VARIABLES:${NC}
    CLICKUP_API_KEY    Your ClickUp API token (required)
    CLICKUP_LIST_ID    Default ClickUp list ID to process (optional)

${YELLOW}OPTIONS:${NC}
    -h, --help           Show this help message
    -d, --dry-run        Preview changes without applying them
    -l, --list-id ID     Specify the list ID (overrides CLICKUP_LIST_ID env var)
    -f, --field-name NAME  Custom field name to update (default: PM.Prio)

${YELLOW}ARGUMENTS:${NC}
    LIST_ID            ClickUp list ID to process (overrides CLICKUP_LIST_ID env var)
                       Can be provided as a positional argument or via --list-id option

${YELLOW}EXAMPLES:${NC}
    # Using environment variables only
    export CLICKUP_API_KEY="your-api-key"
    export CLICKUP_LIST_ID="123456789"
    $(basename "$0")

    # Override list ID with positional argument
    export CLICKUP_API_KEY="your-api-key"
    $(basename "$0") 123456789

    # Override list ID with option flag
    export CLICKUP_API_KEY="your-api-key"
    $(basename "$0") --list-id 123456789

    # Dry run to preview changes
    $(basename "$0") --dry-run 123456789

    # Combine all options
    $(basename "$0") --dry-run --list-id 123456789

    # Use a different custom field
    $(basename "$0") --field-name "Priority" 123456789

${YELLOW}SETUP:${NC}
    1. Get your ClickUp API token from: https://app.clickup.com/settings/apps
    2. Set the CLICKUP_API_KEY environment variable:
       export CLICKUP_API_KEY="your-api-key-here"
    3. (Optional) Set default list ID:
       export CLICKUP_LIST_ID="your-list-id-here"

${YELLOW}NOTES:${NC}
    - API key must be provided via CLICKUP_API_KEY environment variable
    - List ID can be provided via environment variable, command-line option, or argument
    - Command-line list ID takes precedence over environment variable
    - Use --dry-run to preview changes before applying them
    - The script updates a custom field (PM.Prio by default), not task names
    - Ensure the custom field exists on all tasks before running

EOF
}

# Initialize variables
DRY_RUN=""
LIST_ID_ARG=""
FIELD_NAME="PM.Prio"

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -d|--dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        -l|--list-id)
            LIST_ID_ARG="$2"
            shift 2
            ;;
        -f|--field-name)
            FIELD_NAME="$2"
            shift 2
            ;;
        -*)
            echo -e "${RED}Error: Unknown option $1${NC}" >&2
            echo "Use --help for usage information"
            exit 1
            ;;
        *)
            # Positional argument - assume it's the list ID
            if [ -z "$LIST_ID_ARG" ]; then
                LIST_ID_ARG="$1"
            else
                echo -e "${RED}Error: Multiple list IDs specified${NC}" >&2
                exit 1
            fi
            shift
            ;;
    esac
done

# Check for required API key
if [ -z "$CLICKUP_API_KEY" ]; then
    echo -e "${RED}Error: CLICKUP_API_KEY environment variable is not set${NC}" >&2
    echo ""
    echo "Please set your ClickUp API key:"
    echo "  export CLICKUP_API_KEY=\"your-api-key-here\""
    echo ""
    echo "Get your API key from: https://app.clickup.com/settings/apps"
    echo ""
    echo "Use --help for more information"
    exit 1
fi

# Determine which list ID to use (command-line arg overrides env var)
if [ -n "$LIST_ID_ARG" ]; then
    LIST_ID="$LIST_ID_ARG"
elif [ -n "$CLICKUP_LIST_ID" ]; then
    LIST_ID="$CLICKUP_LIST_ID"
else
    echo -e "${RED}Error: No list ID provided${NC}" >&2
    echo ""
    echo "Provide a list ID either:"
    echo "  1. As an argument: $(basename "$0") 123456789"
    echo "  2. Via option: $(basename "$0") --list-id 123456789"
    echo "  3. Via environment variable: export CLICKUP_LIST_ID=\"123456789\""
    echo ""
    echo "Use --help for more information"
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if Python script exists
PYTHON_SCRIPT="$SCRIPT_DIR/clickup_numbering.py"
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}Error: clickup_numbering.py not found at $PYTHON_SCRIPT${NC}" >&2
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed or not in PATH${NC}" >&2
    exit 1
fi

# Display configuration
echo -e "${BLUE}ClickUp Task Numbering${NC}"
echo -e "${BLUE}=====================${NC}"
echo "List ID: $LIST_ID"
echo "Custom Field: $FIELD_NAME"
if [ -n "$DRY_RUN" ]; then
    echo -e "Mode: ${YELLOW}DRY RUN (no changes will be made)${NC}"
else
    echo -e "Mode: ${GREEN}LIVE (changes will be applied)${NC}"
fi
echo ""

# Run the Python script
python3 "$PYTHON_SCRIPT" \
    --api-token "$CLICKUP_API_KEY" \
    --list-id "$LIST_ID" \
    --field-name "$FIELD_NAME" \
    $DRY_RUN
