# FastMCP Demo: Schedule Planner MCP Server

A comprehensive demonstration of how [FastMCP](https://github.com/jlowin/fastmcp) can transform a Python package into a fully-featured Model Context Protocol (MCP) server.

## Overview

This demo showcases the power of FastMCP by taking a custom `schedule_planner` Python package and exposing its functionality through MCP. The result is a production-ready server that AI assistants can use to manage personal schedules, appointments, and time management tasks.

**Key Demo Features:**
- Complete Python package → MCP server transformation
- 28 MCP tools with NumPy-style documentation
- 2 Resources for read-only data access
- 3 Interactive prompts for common workflows
- Multiple schedule management with state persistence
- Ready for VS Code integration

## The Schedule Planner Package

The `schedule_planner` package is a modular Python library for personal schedule management located in `example_code_base/`.

### Package Features

**Core Components:**
- **Time Periods**: `Day`, `Week`, `Month`, `Year` classes
- **Time Management**: `Time` and `TimeRange` for precise scheduling
- **Event Types**: Six specialized event classes using inheritance:
  - `Appointment` - General appointments
  - `DoctorAppointment` - Medical visits with specialized fields
  - `WorkMeeting` - Professional meetings with agendas
  - `Chore` - Household tasks with recurrence support
  - `GymTime` - Exercise sessions with workout tracking
  - `PersonalEvent` - Flexible personal activities
- **Schedule Management**: Create multiple schedules, detect conflicts, find free time
- **Rich Filtering**: Query by type, priority, status, tags, and date ranges

### Event Properties

All events support:
- **Priority Levels**: LOW, MEDIUM, HIGH, URGENT
- **Status Tracking**: scheduled, in_progress, completed, cancelled, rescheduled
- **Custom Tags**: For flexible categorization
- **Time Ranges**: Precise start/end times with conflict detection

## The MCP Server

Located in `FastMCP_Server/scheduler_server.py`, this server exposes the schedule_planner package through the Model Context Protocol using FastMCP.

### Architecture

```
FastMCP Server
├── State Management (Global)
│   ├── Multiple schedules dictionary
│   └── Active schedule tracking
├── Parsing Layer
│   ├── Day/Month/Year parsing
│   └── Time/TimeRange creation
├── MCP Tools (28 functions)
│   ├── Schedule management (5)
│   ├── Event creation (6)
│   ├── Event queries (9)
│   └── Event modifications (8)
├── MCP Resources (2)
│   ├── schedule://active/summary
│   └── schedule://active/upcoming
└── MCP Prompts (3)
    ├── schedule_meeting_prompt
    ├── daily_schedule_review_prompt
    └── weekly_planning_prompt
```

### Server Features

- **Zero External Dependencies**: Uses only the schedule_planner package
- **Comprehensive Documentation**: NumPy-style docstrings on all tools
- **Type Safety**: Full type hints throughout
- **Error Handling**: Proper validation and helpful error messages
- **Stateful**: Maintains multiple schedules in memory
- **Transport Flexible**: Supports STDIO (default), HTTP, and SSE modes

## Available Tools

The server exposes 28 tools organized by function:

### Schedule Management (5 tools)
- `create_schedule` - Create a new named schedule
- `list_schedules` - View all schedules with statistics
- `set_active_schedule` - Switch between schedules
- `delete_schedule` - Remove a schedule
- `clear_schedule` - Clear all events from active schedule

### Event Creation (6 tools)
- `create_appointment` - General appointments with location/attendees
- `create_doctor_appointment` - Medical appointments with doctor info
- `create_work_meeting` - Professional meetings with agendas/links
- `create_chore` - Household tasks with recurrence
- `create_gym_session` - Workouts with exercise tracking
- `create_personal_event` - Flexible personal activities

### Event Queries (9 tools)
- `get_events_on_day` - Events for a specific date
- `get_events_in_date_range` - Events between two dates
- `get_upcoming_events` - Future events with limit
- `get_events_by_type` - Filter by event type
- `get_events_by_priority` - Filter by priority level
- `get_events_by_status` - Filter by status
- `get_events_by_tag` - Filter by custom tags
- `check_conflicts` - Check for scheduling conflicts
- `get_free_time_slots` - Find available time slots
- `get_schedule_statistics` - Comprehensive schedule metrics
- `get_busiest_days` - Identify overloaded days

### Event Modifications (5 tools)
- `update_event_status` - Change event status
- `update_event_priority` - Adjust priority level
- `add_tags_to_event` - Add custom tags
- `remove_tags_from_event` - Remove tags
- `delete_event` - Remove an event

## Resources

The server provides 2 read-only resources:

- **`schedule://active/summary`** - Active schedule summary with statistics
- **`schedule://active/upcoming`** - Formatted list of upcoming events

## Prompts

3 interactive prompts for common workflows:

- **`schedule_meeting_prompt`** - Interactive meeting scheduling with conflict checking
- **`daily_schedule_review_prompt`** - Comprehensive daily schedule review
- **`weekly_planning_prompt`** - Weekly planning and overview

## Installation & Setup

### Prerequisites

- Python 3.12+ (recommended, 3.9+ minimum)
- FastMCP library

### Install Dependencies

```bash
# Create and activate virtual environment (optional but recommended)
python -m venv .venv3.12
source .venv3.12/bin/activate  # On Linux/Mac
# .venv3.12\Scripts\activate  # On Windows

# Install required packages
pip install -r FastMCP_Server/requirements.txt
```

### Verify Installation

```bash
python verify_server.py
```

## Deploying as STDIO in VS Code

### Step 1: Configure VS Code Settings

Add the server to your VS Code MCP settings file:

**Location:** `~/.config/mcp_settings.json`

```json
{
  "mcpServers": {
    "schedule-planner": {
      "command": "python",
      "args": [
        "/path/to/your/FastMCP_Server/scheduler_server.py"
      ],
      "disabled": false
    }
  }
}
```

### Step 2: Restart VS Code or Reload MCP

After adding the configuration:
1. Restart VS Code, OR
2. Use the command palette (Ctrl+Shift+P) to reload MCP servers

### Step 3: Verify Connection

Your AI assistant should now have access to the schedule planner tools. Test it with:

```bash
"Create a work meeting called 'Team Standup' for tomorrow at 9 AM for 30 minutes"
```

Then try

```bash
"Create me a chronjob shell script that runs after my first work meeting that echoes 'hello world'."
```

You can also try the following:

```bash
"When am I free tomorrow for at least 2 hours?"

"Do I have any conflicts in my schedule?"

"Show me my schedule statistics"
```

## Testing

Test the server functionality:

```bash
# Run comprehensive tests
python FastMCP_Server/test_server.py

# Quick verification
python verify_server.py
```

## Project Structure

```
FastMCP_demo/
├── README.md                          # This file
├── QUICK_REFERENCE.md                 # Quick command reference
├── verify_server.py                   # Server verification script
│
├── example_code_base/                 # Schedule Planner Package
│   ├── README_LIBRARY.md              # Package documentation
│   ├── example_usage.py               # Package usage examples
│   └── schedule_planner/
│       ├── __init__.py
│       ├── events.py                  # Event classes
│       ├── schedule.py                # Schedule management
│       ├── time_of_day.py            # Time handling
│       └── time_periods.py           # Date handling
│
└── FastMCP_Server/                    # MCP Server
    ├── README.md                      # Server documentation
    ├── requirements.txt               # Python dependencies
    ├── scheduler_server.py            # Main MCP server
    ├── test_server.py                # Server tests
    ├── example_client.py             # Client usage example
    └── fastmcp.json                  # FastMCP config
```

**Built with [FastMCP](https://github.com/jlowin/fastmcp)** - The fastest way to build MCP servers in Python.
