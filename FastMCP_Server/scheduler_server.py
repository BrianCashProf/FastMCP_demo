#!/usr/bin/env python3
"""
Schedule Planner MCP Server

This FastMCP server provides Model Context Protocol access to the schedule_planner library,
allowing AI assistants to manage personal schedules, events, appointments, and time management.

Features:
- Create and manage various event types (appointments, meetings, chores, gym sessions)
- Query events by date ranges, types, priorities, and tags
- Check for scheduling conflicts
- Find free time slots
- Generate schedule statistics
- Multiple schedule management

The server uses FastMCP features including:
- Tools with comprehensive NumPy-style docstrings
- Resources for schedule data access
- Prompts for common scheduling tasks
- Context management for state persistence
"""

import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, date

# Add the example_code_base to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "example_code_base"))

from fastmcp import FastMCP

from schedule_planner import (
    Day, Week, Month, Year,
    Time, TimeRange,
    Event, Appointment, DoctorAppointment, Chore, WorkMeeting, GymTime, PersonalEvent,
    EventPriority, EventStatus,
    Schedule
)

# Initialize FastMCP server
mcp = FastMCP("Schedule Planner")

# Global state for managing multiple schedules
schedules: Dict[str, Schedule] = {}
active_schedule_name: str = "default"

# Initialize default schedule
schedules["default"] = Schedule("Default Schedule")


def get_active_schedule() -> Schedule:
    """Get the currently active schedule."""
    return schedules[active_schedule_name]


def parse_day(year: int, month: int, day: int) -> Day:
    """
    Parse and create a Day object.
    
    Parameters
    ----------
    year : int
        The year (e.g., 2025)
    month : int
        The month (1-12)
    day : int
        The day of the month (1-31)
    
    Returns
    -------
    Day
        A Day object representing the specified date
    
    Raises
    ------
    ValueError
        If the date is invalid
    """
    return Day(year, month, day)


def parse_time(hour: int, minute: int = 0) -> Time:
    """
    Parse and create a Time object.
    
    Parameters
    ----------
    hour : int
        The hour (0-23)
    minute : int, optional
        The minute (0-59), default is 0
    
    Returns
    -------
    Time
        A Time object representing the specified time
    
    Raises
    ------
    ValueError
        If the time values are out of valid range
    """
    return Time(hour, minute)


# ============================================================================
# Schedule Management Tools
# ============================================================================

@mcp.tool()
def create_schedule(name: str) -> str:
    """
    Create a new named schedule.
    
    This tool creates a new schedule that can be used to organize events
    separately from other schedules. Each schedule maintains its own
    collection of events and can be switched between using set_active_schedule.
    
    Parameters
    ----------
    name : str
        The name for the new schedule. Must be unique.
    
    Returns
    -------
    str
        Success message with the schedule name
    
    Raises
    ------
    ValueError
        If a schedule with the given name already exists
    
    Examples
    --------
    >>> create_schedule("Work Schedule")
    'Created schedule: Work Schedule'
    
    >>> create_schedule("Personal Schedule")
    'Created schedule: Personal Schedule'
    
    Notes
    -----
    After creating a schedule, use set_active_schedule() to switch to it
    before adding events.
    
    See Also
    --------
    list_schedules : List all available schedules
    set_active_schedule : Switch to a different schedule
    delete_schedule : Remove a schedule
    """
    if name in schedules:
        raise ValueError(f"Schedule '{name}' already exists")
    
    schedules[name] = Schedule(name)
    return f"Created schedule: {name}"


@mcp.tool()
def list_schedules() -> List[Dict[str, Any]]:
    """
    List all available schedules with their statistics.
    
    Returns
    -------
    list of dict
        A list of dictionaries, each containing:
        - name : str
            The schedule name
        - is_active : bool
            Whether this is the currently active schedule
        - total_events : int
            Total number of events in the schedule
        - upcoming_events : int
            Number of upcoming events
    
    Examples
    --------
    >>> list_schedules()
    [
        {
            'name': 'default',
            'is_active': True,
            'total_events': 5,
            'upcoming_events': 3
        },
        {
            'name': 'Work Schedule',
            'is_active': False,
            'total_events': 12,
            'upcoming_events': 8
        }
    ]
    
    See Also
    --------
    create_schedule : Create a new schedule
    set_active_schedule : Switch to a different schedule
    """
    result = []
    for name, schedule in schedules.items():
        stats = schedule.get_statistics()
        result.append({
            "name": name,
            "is_active": name == active_schedule_name,
            "total_events": stats["total_events"],
            "upcoming_events": stats["upcoming_events"]
        })
    return result


@mcp.tool()
def set_active_schedule(name: str) -> str:
    """
    Switch to a different schedule.
    
    Sets the specified schedule as active. All subsequent operations
    will be performed on this schedule until switched again.
    
    Parameters
    ----------
    name : str
        The name of the schedule to activate
    
    Returns
    -------
    str
        Confirmation message
    
    Raises
    ------
    ValueError
        If the schedule name does not exist
    
    Examples
    --------
    >>> set_active_schedule("Work Schedule")
    'Active schedule set to: Work Schedule'
    
    See Also
    --------
    list_schedules : View all available schedules
    create_schedule : Create a new schedule
    """
    global active_schedule_name
    
    if name not in schedules:
        raise ValueError(f"Schedule '{name}' does not exist")
    
    active_schedule_name = name
    return f"Active schedule set to: {name}"


@mcp.tool()
def delete_schedule(name: str) -> str:
    """
    Delete a schedule.
    
    Permanently removes a schedule and all its events. The default schedule
    cannot be deleted. If deleting the active schedule, switches to default.
    
    Parameters
    ----------
    name : str
        The name of the schedule to delete
    
    Returns
    -------
    str
        Confirmation message
    
    Raises
    ------
    ValueError
        If the schedule does not exist or attempting to delete default schedule
    
    Examples
    --------
    >>> delete_schedule("Old Schedule")
    'Deleted schedule: Old Schedule'
    
    Notes
    -----
    This operation cannot be undone. All events in the schedule will be lost.
    
    See Also
    --------
    create_schedule : Create a new schedule
    clear_schedule : Remove all events but keep the schedule
    """
    global active_schedule_name
    
    if name not in schedules:
        raise ValueError(f"Schedule '{name}' does not exist")
    
    if name == "default":
        raise ValueError("Cannot delete the default schedule")
    
    del schedules[name]
    
    # If we deleted the active schedule, switch to default
    if name == active_schedule_name:
        active_schedule_name = "default"
    
    return f"Deleted schedule: {name}"


@mcp.tool()
def clear_schedule() -> str:
    """
    Remove all events from the active schedule.
    
    This tool clears all events from the currently active schedule while
    keeping the schedule itself. This is useful for starting fresh or
    removing test data.
    
    Returns
    -------
    str
        Confirmation message
    
    Examples
    --------
    >>> clear_schedule()
    'Cleared all events from schedule: Work Schedule'
    
    Notes
    -----
    This operation cannot be undone. Consider using delete_event() for
    individual event removal instead.
    
    See Also
    --------
    delete_schedule : Delete the entire schedule
    """
    schedule = get_active_schedule()
    schedule.clear_all_events()
    return f"Cleared all events from schedule: {schedule.name}"


# ============================================================================
# Event Creation Tools
# ============================================================================

@mcp.tool()
def create_appointment(
    title: str,
    year: int,
    month: int,
    day: int,
    start_hour: int,
    start_minute: int,
    end_hour: int,
    end_minute: int,
    location: str = "",
    description: str = "",
    priority: str = "MEDIUM",
    attendees: Optional[List[str]] = None,
    reminder_minutes: int = 15
) -> Dict[str, Any]:
    """
    Create a general appointment.
    
    Creates an appointment event and adds it to the active schedule.
    Appointments are suitable for general meetings, scheduled calls,
    or any time-based commitment.
    
    Parameters
    ----------
    title : str
        The title/name of the appointment
    year : int
        Year of the appointment (e.g., 2025)
    month : int
        Month of the appointment (1-12)
    day : int
        Day of the month (1-31)
    start_hour : int
        Starting hour (0-23)
    start_minute : int
        Starting minute (0-59)
    end_hour : int
        Ending hour (0-23)
    end_minute : int
        Ending minute (0-59)
    location : str, optional
        Where the appointment takes place
    description : str, optional
        Detailed description of the appointment
    priority : str, optional
        Priority level: 'LOW', 'MEDIUM', 'HIGH', or 'URGENT' (default: 'MEDIUM')
    attendees : list of str, optional
        List of people attending the appointment
    reminder_minutes : int, optional
        Minutes before the event to send a reminder (default: 15)
    
    Returns
    -------
    dict
        Dictionary representation of the created appointment with all fields
    
    Raises
    ------
    ValueError
        If date or time values are invalid, or priority is not recognized
    
    Examples
    --------
    >>> create_appointment(
    ...     title="Team Sync",
    ...     year=2025, month=10, day=25,
    ...     start_hour=14, start_minute=0,
    ...     end_hour=15, end_minute=0,
    ...     location="Conference Room A",
    ...     priority="HIGH",
    ...     attendees=["Alice", "Bob"]
    ... )
    {
        'type': 'Appointment',
        'title': 'Team Sync',
        'day': 'Friday, October 25, 2025',
        'time_range': '2:00 PM - 3:00 PM',
        ...
    }
    
    Notes
    -----
    The appointment is automatically added to the active schedule.
    Use check_conflicts() to verify no scheduling conflicts exist.
    
    See Also
    --------
    create_doctor_appointment : Create a medical appointment
    create_work_meeting : Create a work meeting with agenda
    check_conflicts : Check for scheduling conflicts
    """
    schedule = get_active_schedule()
    event_day = parse_day(year, month, day)
    time_range = TimeRange(
        parse_time(start_hour, start_minute),
        parse_time(end_hour, end_minute)
    )
    
    appointment = Appointment(
        title=title,
        day=event_day,
        time_range=time_range,
        location=location,
        description=description,
        priority=EventPriority[priority],
        attendees=attendees or [],
        reminder_minutes=reminder_minutes
    )
    
    schedule.add_event(appointment)
    return appointment.to_dict()


@mcp.tool()
def create_doctor_appointment(
    title: str,
    year: int,
    month: int,
    day: int,
    start_hour: int,
    start_minute: int,
    end_hour: int,
    end_minute: int,
    doctor_name: str = "",
    specialty: str = "",
    location: str = "",
    description: str = "",
    insurance_required: bool = True,
    medical_notes: str = ""
) -> Dict[str, Any]:
    """
    Create a medical appointment.
    
    Creates a specialized doctor appointment with medical-specific fields.
    Doctor appointments are automatically set to HIGH priority by default.
    
    Parameters
    ----------
    title : str
        The title of the appointment (e.g., "Annual Checkup")
    year : int
        Year of the appointment
    month : int
        Month of the appointment (1-12)
    day : int
        Day of the month (1-31)
    start_hour : int
        Starting hour (0-23)
    start_minute : int
        Starting minute (0-59)
    end_hour : int
        Ending hour (0-23)
    end_minute : int
        Ending minute (0-59)
    doctor_name : str, optional
        Name of the doctor
    specialty : str, optional
        Medical specialty (e.g., "Cardiology", "General Practice")
    location : str, optional
        Medical facility location
    description : str, optional
        Description of the visit purpose
    insurance_required : bool, optional
        Whether insurance information is needed (default: True)
    medical_notes : str, optional
        Medical-specific notes (e.g., "Bring X-ray results")
    
    Returns
    -------
    dict
        Dictionary representation of the created doctor appointment
    
    Examples
    --------
    >>> create_doctor_appointment(
    ...     title="Annual Physical",
    ...     year=2025, month=11, day=15,
    ...     start_hour=10, start_minute=0,
    ...     end_hour=11, end_minute=0,
    ...     doctor_name="Dr. Smith",
    ...     specialty="General Practice",
    ...     location="Downtown Medical Center",
    ...     medical_notes="Bring previous test results"
    ... )
    
    Notes
    -----
    Doctor appointments are automatically given HIGH priority.
    Remember to bring insurance cards if insurance_required is True.
    
    See Also
    --------
    create_appointment : Create a general appointment
    get_events_by_priority : Filter events by priority level
    """
    schedule = get_active_schedule()
    event_day = parse_day(year, month, day)
    time_range = TimeRange(
        parse_time(start_hour, start_minute),
        parse_time(end_hour, end_minute)
    )
    
    appointment = DoctorAppointment(
        title=title,
        day=event_day,
        time_range=time_range,
        doctor_name=doctor_name,
        specialty=specialty,
        location=location,
        description=description,
        insurance_required=insurance_required,
        medical_notes=medical_notes
    )
    
    schedule.add_event(appointment)
    return appointment.to_dict()


@mcp.tool()
def create_work_meeting(
    title: str,
    year: int,
    month: int,
    day: int,
    start_hour: int,
    start_minute: int,
    end_hour: int,
    end_minute: int,
    organizer: str = "",
    is_virtual: bool = True,
    meeting_link: str = "",
    room: str = "",
    description: str = "",
    priority: str = "MEDIUM",
    attendees: Optional[List[str]] = None,
    agenda: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a work meeting.
    
    Creates a professional meeting event with support for agendas,
    attendees, and virtual/physical location tracking.
    
    Parameters
    ----------
    title : str
        The meeting title
    year : int
        Year of the meeting
    month : int
        Month of the meeting (1-12)
    day : int
        Day of the month (1-31)
    start_hour : int
        Starting hour (0-23)
    start_minute : int
        Starting minute (0-59)
    end_hour : int
        Ending hour (0-23)
    end_minute : int
        Ending minute (0-59)
    organizer : str, optional
        Person organizing the meeting
    is_virtual : bool, optional
        Whether the meeting is virtual (default: True)
    meeting_link : str, optional
        URL for virtual meeting (e.g., Zoom, Teams link)
    room : str, optional
        Physical meeting room if not virtual
    description : str, optional
        Meeting description or purpose
    priority : str, optional
        Priority level: 'LOW', 'MEDIUM', 'HIGH', or 'URGENT'
    attendees : list of str, optional
        List of meeting attendees
    agenda : list of str, optional
        List of agenda items
    
    Returns
    -------
    dict
        Dictionary representation of the created work meeting
    
    Examples
    --------
    >>> create_work_meeting(
    ...     title="Q4 Planning",
    ...     year=2025, month=10, day=30,
    ...     start_hour=14, start_minute=0,
    ...     end_hour=15, end_minute=30,
    ...     organizer="Jane Manager",
    ...     meeting_link="https://zoom.us/j/123456",
    ...     attendees=["Alice", "Bob", "Charlie"],
    ...     agenda=["Review Q3", "Set Q4 goals", "Budget"]
    ... )
    
    Notes
    -----
    For virtual meetings, include the meeting_link.
    For physical meetings, set is_virtual=False and specify room.
    
    See Also
    --------
    create_appointment : Create a general appointment
    add_meeting_agenda_item : Add agenda items after creation
    """
    schedule = get_active_schedule()
    event_day = parse_day(year, month, day)
    time_range = TimeRange(
        parse_time(start_hour, start_minute),
        parse_time(end_hour, end_minute)
    )
    
    meeting = WorkMeeting(
        title=title,
        day=event_day,
        time_range=time_range,
        organizer=organizer,
        is_virtual=is_virtual,
        meeting_link=meeting_link,
        room=room,
        description=description,
        priority=EventPriority[priority],
        attendees=attendees or [],
        agenda=agenda or []
    )
    
    schedule.add_event(meeting)
    return meeting.to_dict()


@mcp.tool()
def create_chore(
    title: str,
    year: int,
    month: int,
    day: int,
    start_hour: int,
    start_minute: int,
    duration_minutes: int,
    category: str = "General",
    is_recurring: bool = False,
    recurrence_days: int = 7,
    estimated_effort: str = "Medium",
    description: str = "",
    priority: str = "MEDIUM"
) -> Dict[str, Any]:
    """
    Create a household chore or task.
    
    Creates a chore event for tracking household tasks. Supports
    recurring chores that repeat at regular intervals.
    
    Parameters
    ----------
    title : str
        The chore title (e.g., "Grocery Shopping", "Clean Kitchen")
    year : int
        Year of the chore
    month : int
        Month of the chore (1-12)
    day : int
        Day of the month (1-31)
    start_hour : int
        Starting hour (0-23)
    start_minute : int
        Starting minute (0-59)
    duration_minutes : int
        Expected duration in minutes
    category : str, optional
        Chore category (e.g., "Cleaning", "Shopping", "Maintenance")
        Default: "General"
    is_recurring : bool, optional
        Whether this chore repeats (default: False)
    recurrence_days : int, optional
        Days between recurrences if recurring (default: 7)
    estimated_effort : str, optional
        Effort level: "Low", "Medium", or "High" (default: "Medium")
    description : str, optional
        Detailed description of the chore
    priority : str, optional
        Priority level: 'LOW', 'MEDIUM', 'HIGH', or 'URGENT'
    
    Returns
    -------
    dict
        Dictionary representation of the created chore
    
    Examples
    --------
    >>> create_chore(
    ...     title="Weekly Grocery Shopping",
    ...     year=2025, month=10, day=26,
    ...     start_hour=18, start_minute=0,
    ...     duration_minutes=60,
    ...     category="Shopping",
    ...     is_recurring=True,
    ...     recurrence_days=7
    ... )
    
    >>> create_chore(
    ...     title="Deep Clean Bathroom",
    ...     year=2025, month=10, day=27,
    ...     start_hour=10, start_minute=0,
    ...     duration_minutes=90,
    ...     category="Cleaning",
    ...     estimated_effort="High"
    ... )
    
    Notes
    -----
    Recurring chores automatically calculate the next occurrence date.
    Use get_next_chore_occurrence() to find when it repeats.
    
    See Also
    --------
    create_personal_event : Create other personal activities
    get_events_by_type : Filter events by type
    """
    schedule = get_active_schedule()
    event_day = parse_day(year, month, day)
    end_time = parse_time(start_hour, start_minute).add_minutes(duration_minutes)
    time_range = TimeRange(
        parse_time(start_hour, start_minute),
        end_time
    )
    
    chore = Chore(
        title=title,
        day=event_day,
        time_range=time_range,
        category=category,
        is_recurring=is_recurring,
        recurrence_days=recurrence_days,
        estimated_effort=estimated_effort,
        description=description,
        priority=EventPriority[priority]
    )
    
    schedule.add_event(chore)
    return chore.to_dict()


@mcp.tool()
def create_gym_session(
    title: str,
    year: int,
    month: int,
    day: int,
    start_hour: int,
    start_minute: int,
    duration_minutes: int,
    workout_type: str = "General",
    gym_location: str = "",
    trainer: str = "",
    exercises: Optional[List[str]] = None,
    target_calories: int = 0,
    description: str = "",
    priority: str = "MEDIUM"
) -> Dict[str, Any]:
    """
    Create a gym or exercise session.
    
    Creates a workout event to track exercise activities, including
    workout type, exercises, and fitness goals.
    
    Parameters
    ----------
    title : str
        The workout title (e.g., "Morning Cardio", "Leg Day")
    year : int
        Year of the workout
    month : int
        Month of the workout (1-12)
    day : int
        Day of the month (1-31)
    start_hour : int
        Starting hour (0-23)
    start_minute : int
        Starting minute (0-59)
    duration_minutes : int
        Expected workout duration in minutes
    workout_type : str, optional
        Type of workout (e.g., "Cardio", "Strength", "Yoga", "HIIT")
        Default: "General"
    gym_location : str, optional
        Name or location of the gym
    trainer : str, optional
        Personal trainer name if applicable
    exercises : list of str, optional
        List of exercises to perform
    target_calories : int, optional
        Target calories to burn (default: 0)
    description : str, optional
        Workout description or goals
    priority : str, optional
        Priority level: 'LOW', 'MEDIUM', 'HIGH', or 'URGENT'
    
    Returns
    -------
    dict
        Dictionary representation of the created gym session
    
    Examples
    --------
    >>> create_gym_session(
    ...     title="Upper Body Strength",
    ...     year=2025, month=10, day=26,
    ...     start_hour=6, start_minute=30,
    ...     duration_minutes=60,
    ...     workout_type="Strength Training",
    ...     gym_location="FitLife Gym",
    ...     exercises=["Bench Press", "Pull-ups", "Shoulder Press"],
    ...     target_calories=400
    ... )
    
    >>> create_gym_session(
    ...     title="Morning Run",
    ...     year=2025, month=10, day=27,
    ...     start_hour=6, start_minute=0,
    ...     duration_minutes=45,
    ...     workout_type="Cardio",
    ...     target_calories=500
    ... )
    
    Notes
    -----
    Track your fitness progress by recording completed gym sessions.
    Use tags to categorize workouts by muscle groups or goals.
    
    See Also
    --------
    create_personal_event : Create other personal activities
    add_tags_to_event : Tag events for better organization
    """
    schedule = get_active_schedule()
    event_day = parse_day(year, month, day)
    end_time = parse_time(start_hour, start_minute).add_minutes(duration_minutes)
    time_range = TimeRange(
        parse_time(start_hour, start_minute),
        end_time
    )
    
    gym_time = GymTime(
        title=title,
        day=event_day,
        time_range=time_range,
        workout_type=workout_type,
        gym_location=gym_location,
        trainer=trainer,
        exercises=exercises or [],
        target_calories=target_calories,
        description=description,
        priority=EventPriority[priority]
    )
    
    schedule.add_event(gym_time)
    return gym_time.to_dict()


@mcp.tool()
def create_personal_event(
    title: str,
    year: int,
    month: int,
    day: int,
    start_hour: int,
    start_minute: int,
    duration_minutes: int,
    category: str = "General",
    location: str = "",
    participants: Optional[List[str]] = None,
    cost: float = 0.0,
    description: str = "",
    priority: str = "MEDIUM"
) -> Dict[str, Any]:
    """
    Create a personal event.
    
    Creates a flexible personal event for activities like hobbies,
    social gatherings, entertainment, or any personal activity.
    
    Parameters
    ----------
    title : str
        The event title
    year : int
        Year of the event
    month : int
        Month of the event (1-12)
    day : int
        Day of the month (1-31)
    start_hour : int
        Starting hour (0-23)
    start_minute : int
        Starting minute (0-59)
    duration_minutes : int
        Expected duration in minutes
    category : str, optional
        Event category (e.g., "Social", "Hobby", "Entertainment")
        Default: "General"
    location : str, optional
        Where the event takes place
    participants : list of str, optional
        Other people involved in the event
    cost : float, optional
        Estimated or actual cost (default: 0.0)
    description : str, optional
        Event description
    priority : str, optional
        Priority level: 'LOW', 'MEDIUM', 'HIGH', or 'URGENT'
    
    Returns
    -------
    dict
        Dictionary representation of the created personal event
    
    Examples
    --------
    >>> create_personal_event(
    ...     title="Movie Night",
    ...     year=2025, month=10, day=26,
    ...     start_hour=19, start_minute=0,
    ...     duration_minutes=150,
    ...     category="Entertainment",
    ...     location="Downtown Cinema",
    ...     participants=["Sarah", "Mike"],
    ...     cost=25.0
    ... )
    
    >>> create_personal_event(
    ...     title="Guitar Practice",
    ...     year=2025, month=10, day=27,
    ...     start_hour=20, start_minute=0,
    ...     duration_minutes=60,
    ...     category="Hobby"
    ... )
    
    Notes
    -----
    Personal events are flexible and can represent any activity.
    Use categories and tags to organize similar events.
    
    See Also
    --------
    create_chore : Create household tasks
    create_gym_session : Create workout sessions
    get_events_by_tag : Find events by tags
    """
    schedule = get_active_schedule()
    event_day = parse_day(year, month, day)
    end_time = parse_time(start_hour, start_minute).add_minutes(duration_minutes)
    time_range = TimeRange(
        parse_time(start_hour, start_minute),
        end_time
    )
    
    event = PersonalEvent(
        title=title,
        day=event_day,
        time_range=time_range,
        category=category,
        location=location,
        participants=participants or [],
        cost=cost,
        description=description,
        priority=EventPriority[priority]
    )
    
    schedule.add_event(event)
    return event.to_dict()


# ============================================================================
# Event Query Tools
# ============================================================================

@mcp.tool()
def get_events_on_day(year: int, month: int, day: int) -> List[Dict[str, Any]]:
    """
    Get all events scheduled on a specific day.
    
    Returns all events from the active schedule that are scheduled on
    the specified date, sorted by start time.
    
    Parameters
    ----------
    year : int
        The year (e.g., 2025)
    month : int
        The month (1-12)
    day : int
        The day of the month (1-31)
    
    Returns
    -------
    list of dict
        List of event dictionaries sorted by start time. Empty list if no events.
    
    Examples
    --------
    >>> get_events_on_day(2025, 10, 26)
    [
        {
            'type': 'Work Meeting',
            'title': 'Team Sync',
            'time_range': '2:00 PM - 3:00 PM',
            ...
        },
        {
            'type': 'Gym Time',
            'title': 'Evening Workout',
            'time_range': '6:00 PM - 7:00 PM',
            ...
        }
    ]
    
    See Also
    --------
    get_events_in_week : Get events for a week
    get_events_in_month : Get events for a month
    get_events_in_date_range : Get events between two dates
    """
    schedule = get_active_schedule()
    event_day = parse_day(year, month, day)
    events = schedule.get_events_on_day(event_day)
    return [event.to_dict() for event in events]


@mcp.tool()
def get_events_in_date_range(
    start_year: int, start_month: int, start_day: int,
    end_year: int, end_month: int, end_day: int
) -> List[Dict[str, Any]]:
    """
    Get all events within a date range.
    
    Returns events scheduled between two dates (inclusive) from the
    active schedule.
    
    Parameters
    ----------
    start_year : int
        Starting year
    start_month : int
        Starting month (1-12)
    start_day : int
        Starting day of the month (1-31)
    end_year : int
        Ending year
    end_month : int
        Ending month (1-12)
    end_day : int
        Ending day of the month (1-31)
    
    Returns
    -------
    list of dict
        List of event dictionaries within the date range
    
    Examples
    --------
    >>> get_events_in_date_range(
    ...     2025, 10, 23,
    ...     2025, 10, 30
    ... )
    # Returns all events between Oct 23 and Oct 30, 2025
    
    Notes
    -----
    Both start and end dates are inclusive.
    Returns events sorted by date and time.
    
    See Also
    --------
    get_upcoming_events : Get future events with a limit
    get_events_on_day : Get events for a specific day
    """
    schedule = get_active_schedule()
    start_day_obj = parse_day(start_year, start_month, start_day)
    end_day_obj = parse_day(end_year, end_month, end_day)
    events = schedule.get_events_in_date_range(start_day_obj, end_day_obj)
    return [event.to_dict() for event in events]


@mcp.tool()
def get_upcoming_events(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get upcoming events starting from today.
    
    Returns future events from the active schedule, sorted by date
    and time. Useful for seeing what's coming up next.
    
    Parameters
    ----------
    limit : int, optional
        Maximum number of events to return (default: 10)
        Set to -1 to get all upcoming events
    
    Returns
    -------
    list of dict
        List of upcoming event dictionaries, sorted chronologically
    
    Examples
    --------
    >>> get_upcoming_events(5)
    # Returns the next 5 upcoming events
    
    >>> get_upcoming_events(-1)
    # Returns all upcoming events
    
    Notes
    -----
    Events are relative to today's date.
    Completed or cancelled events are still included in the count.
    
    See Also
    --------
    get_events_in_date_range : Get events within a specific range
    get_events_by_status : Filter by event status
    """
    schedule = get_active_schedule()
    limit_val = None if limit == -1 else limit
    events = schedule.get_upcoming_events(limit=limit_val)
    return [event.to_dict() for event in events]


@mcp.tool()
def get_events_by_type(event_type: str) -> List[Dict[str, Any]]:
    """
    Get all events of a specific type.
    
    Filters events in the active schedule by their type. Useful for
    seeing all meetings, appointments, chores, etc.
    
    Parameters
    ----------
    event_type : str
        The event type to filter by. Valid types:
        - "Appointment"
        - "Doctor Appointment"
        - "Work Meeting"
        - "Chore"
        - "Gym Time"
        - "Personal Event"
    
    Returns
    -------
    list of dict
        List of event dictionaries matching the specified type
    
    Examples
    --------
    >>> get_events_by_type("Work Meeting")
    # Returns all work meetings
    
    >>> get_events_by_type("Gym Time")
    # Returns all gym sessions
    
    See Also
    --------
    get_events_by_priority : Filter by priority level
    get_events_by_status : Filter by status
    get_events_by_tag : Filter by tags
    """
    schedule = get_active_schedule()
    events = schedule.get_events_by_type(event_type)
    return [event.to_dict() for event in events]


@mcp.tool()
def get_events_by_priority(priority: str) -> List[Dict[str, Any]]:
    """
    Get all events with a specific priority level.
    
    Filters events by their priority. Useful for focusing on
    high-priority or urgent items.
    
    Parameters
    ----------
    priority : str
        The priority level to filter by:
        - "LOW"
        - "MEDIUM"
        - "HIGH"
        - "URGENT"
    
    Returns
    -------
    list of dict
        List of event dictionaries with the specified priority
    
    Examples
    --------
    >>> get_events_by_priority("HIGH")
    # Returns all high-priority events
    
    >>> get_events_by_priority("URGENT")
    # Returns all urgent events
    
    Notes
    -----
    Doctor appointments default to HIGH priority.
    Use this to focus on critical tasks.
    
    See Also
    --------
    get_events_by_type : Filter by event type
    get_events_by_status : Filter by status
    update_event_priority : Change an event's priority
    """
    schedule = get_active_schedule()
    events = schedule.get_events_by_priority(EventPriority[priority])
    return [event.to_dict() for event in events]


@mcp.tool()
def get_events_by_status(status: str) -> List[Dict[str, Any]]:
    """
    Get all events with a specific status.
    
    Filters events by their current status. Useful for tracking
    completed tasks or finding cancelled events.
    
    Parameters
    ----------
    status : str
        The status to filter by:
        - "scheduled" : Events that are scheduled
        - "in_progress" : Events currently happening
        - "completed" : Finished events
        - "cancelled" : Cancelled events
        - "rescheduled" : Events that were moved
    
    Returns
    -------
    list of dict
        List of event dictionaries with the specified status
    
    Examples
    --------
    >>> get_events_by_status("completed")
    # Returns all completed events
    
    >>> get_events_by_status("scheduled")
    # Returns all scheduled (not yet started) events
    
    See Also
    --------
    mark_event_completed : Mark an event as completed
    mark_event_cancelled : Mark an event as cancelled
    get_events_by_priority : Filter by priority level
    """
    schedule = get_active_schedule()
    # Convert string to EventStatus enum
    status_map = {
        "scheduled": EventStatus.SCHEDULED,
        "in_progress": EventStatus.IN_PROGRESS,
        "completed": EventStatus.COMPLETED,
        "cancelled": EventStatus.CANCELLED,
        "rescheduled": EventStatus.RESCHEDULED
    }
    events = schedule.get_events_by_status(status_map[status.lower()])
    return [event.to_dict() for event in events]


@mcp.tool()
def get_events_by_tag(tag: str) -> List[Dict[str, Any]]:
    """
    Get all events that have a specific tag.
    
    Filters events by tags. Tags are useful for custom categorization
    and grouping related events.
    
    Parameters
    ----------
    tag : str
        The tag to search for
    
    Returns
    -------
    list of dict
        List of event dictionaries that have the specified tag
    
    Examples
    --------
    >>> get_events_by_tag("important")
    # Returns all events tagged as "important"
    
    >>> get_events_by_tag("client-meeting")
    # Returns all client meeting events
    
    Notes
    -----
    Tags are case-sensitive.
    Events can have multiple tags.
    
    See Also
    --------
    add_tags_to_event : Add tags to an event
    remove_tags_from_event : Remove tags from an event
    """
    schedule = get_active_schedule()
    events = schedule.get_events_by_tag(tag)
    return [event.to_dict() for event in events]


@mcp.tool()
def check_conflicts(
    year: int, month: int, day: int,
    start_hour: int, start_minute: int,
    end_hour: int, end_minute: int
) -> Dict[str, Any]:
    """
    Check for scheduling conflicts at a specific time.
    
    Determines if scheduling an event at the specified time would
    conflict with existing events in the active schedule.
    
    Parameters
    ----------
    year : int
        Year to check
    month : int
        Month to check (1-12)
    day : int
        Day to check (1-31)
    start_hour : int
        Starting hour (0-23)
    start_minute : int
        Starting minute (0-59)
    end_hour : int
        Ending hour (0-23)
    end_minute : int
        Ending minute (0-59)
    
    Returns
    -------
    dict
        Dictionary containing:
        - has_conflicts : bool
            Whether conflicts exist
        - conflict_count : int
            Number of conflicting events
        - conflicts : list of dict
            Details of conflicting events
    
    Examples
    --------
    >>> check_conflicts(
    ...     2025, 10, 26,
    ...     14, 0,
    ...     15, 0
    ... )
    {
        'has_conflicts': True,
        'conflict_count': 1,
        'conflicts': [
            {
                'title': 'Team Meeting',
                'time_range': '2:00 PM - 3:00 PM',
                ...
            }
        ]
    }
    
    Notes
    -----
    Use this before scheduling important events to avoid double-booking.
    Conflicts occur when time ranges overlap on the same day.
    
    See Also
    --------
    get_free_time_slots : Find available time slots
    create_appointment : Create an appointment (can check conflicts)
    """
    from schedule_planner.events import Event
    
    schedule = get_active_schedule()
    event_day = parse_day(year, month, day)
    time_range = TimeRange(
        parse_time(start_hour, start_minute),
        parse_time(end_hour, end_minute)
    )
    
    # Create a temporary event for conflict checking
    temp_event = Appointment(
        title="Temp",
        day=event_day,
        time_range=time_range
    )
    
    conflicts = schedule.get_conflicting_events(temp_event)
    
    return {
        "has_conflicts": len(conflicts) > 0,
        "conflict_count": len(conflicts),
        "conflicts": [event.to_dict() for event in conflicts]
    }


@mcp.tool()
def get_free_time_slots(
    year: int, month: int, day: int,
    min_duration_minutes: int = 60
) -> List[Dict[str, str]]:
    """
    Find free time slots on a specific day.
    
    Analyzes the schedule for a given day and identifies available
    time slots where no events are scheduled. Useful for finding
    time to schedule new events.
    
    Parameters
    ----------
    year : int
        Year to check
    month : int
        Month to check (1-12)
    day : int
        Day to check (1-31)
    min_duration_minutes : int, optional
        Minimum duration for a free slot in minutes (default: 60)
        Only slots at least this long will be returned
    
    Returns
    -------
    list of dict
        List of free time slots, each containing:
        - start_time : str
            Start time in 12-hour format
        - end_time : str
            End time in 12-hour format
        - duration_minutes : int
            Duration of the slot
    
    Examples
    --------
    >>> get_free_time_slots(2025, 10, 26, min_duration_minutes=90)
    [
        {
            'start_time': '9:00 AM',
            'end_time': '12:00 PM',
            'duration_minutes': 180
        },
        {
            'start_time': '3:00 PM',
            'end_time': '5:00 PM',
            'duration_minutes': 120
        }
    ]
    
    Notes
    -----
    Default working hours are 9:00 AM to 9:00 PM.
    Smaller min_duration_minutes values may return more slots.
    
    See Also
    --------
    check_conflicts : Check for conflicts at a specific time
    get_events_on_day : See all events on a day
    """
    schedule = get_active_schedule()
    event_day = parse_day(year, month, day)
    free_slots = schedule.get_free_time_slots(event_day, min_duration_minutes)
    
    return [
        {
            "start_time": slot.to_12_hour_format().split(" - ")[0],
            "end_time": slot.to_12_hour_format().split(" - ")[1],
            "duration_minutes": slot.duration_minutes
        }
        for slot in free_slots
    ]


@mcp.tool()
def get_schedule_statistics() -> Dict[str, Any]:
    """
    Get statistics about the active schedule.
    
    Returns comprehensive statistics including event counts, types,
    statuses, and time metrics for the active schedule.
    
    Returns
    -------
    dict
        Dictionary containing:
        - total_events : int
            Total number of events
        - upcoming_events : int
            Number of future events
        - completed_events : int
            Number of completed events
        - cancelled_events : int
            Number of cancelled events
        - events_by_type : dict
            Count of events per type
        - total_scheduled_minutes : int
            Total time scheduled
        - average_event_duration : float
            Average event length in minutes
    
    Examples
    --------
    >>> get_schedule_statistics()
    {
        'total_events': 25,
        'upcoming_events': 15,
        'completed_events': 8,
        'cancelled_events': 2,
        'events_by_type': {
            'Work Meeting': 10,
            'Gym Time': 5,
            'Appointment': 7,
            'Chore': 3
        },
        'total_scheduled_minutes': 3000,
        'average_event_duration': 120.0
    }
    
    See Also
    --------
    get_busiest_days : Find days with most events
    list_schedules : See statistics for all schedules
    """
    schedule = get_active_schedule()
    return schedule.get_statistics()


@mcp.tool()
def get_busiest_days(limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get the days with the most events scheduled.
    
    Identifies which days in the active schedule are busiest based
    on event count. Useful for workload balancing.
    
    Parameters
    ----------
    limit : int, optional
        Number of days to return (default: 5)
    
    Returns
    -------
    list of dict
        List of dictionaries, each containing:
        - day : str
            The day description
        - event_count : int
            Number of events on that day
        - date : str
            Date in YYYY-MM-DD format
    
    Examples
    --------
    >>> get_busiest_days(3)
    [
        {
            'day': 'Monday, October 28, 2025',
            'event_count': 8,
            'date': '2025-10-28'
        },
        {
            'day': 'Wednesday, October 30, 2025',
            'event_count': 6,
            'date': '2025-10-30'
        },
        {
            'day': 'Friday, November 1, 2025',
            'event_count': 5,
            'date': '2025-11-01'
        }
    ]
    
    Notes
    -----
    Consider redistributing events if certain days are overloaded.
    
    See Also
    --------
    get_schedule_statistics : Overall schedule metrics
    get_events_on_day : View events for a specific day
    """
    schedule = get_active_schedule()
    busiest = schedule.get_busiest_days(limit)
    
    return [
        {
            "day": str(day),
            "event_count": count,
            "date": day.date.isoformat()
        }
        for day, count in busiest
    ]


# ============================================================================
# Event Modification Tools
# ============================================================================

@mcp.tool()
def update_event_status(
    event_title: str,
    new_status: str
) -> Dict[str, Any]:
    """
    Update the status of an event.
    
    Changes the status of an event (e.g., mark as completed, cancelled).
    Searches for the event by title in the active schedule.
    
    Parameters
    ----------
    event_title : str
        The title of the event to update
    new_status : str
        The new status:
        - "scheduled" : Mark as scheduled
        - "in_progress" : Mark as in progress
        - "completed" : Mark as completed
        - "cancelled" : Mark as cancelled
    
    Returns
    -------
    dict
        Updated event dictionary
    
    Raises
    ------
    ValueError
        If event not found or status is invalid
    
    Examples
    --------
    >>> update_event_status("Team Meeting", "completed")
    # Marks the "Team Meeting" event as completed
    
    >>> update_event_status("Doctor Appointment", "cancelled")
    # Marks the appointment as cancelled
    
    Notes
    -----
    If multiple events have the same title, updates the first match.
    Consider using more specific titles for better targeting.
    
    See Also
    --------
    get_events_by_status : Filter events by status
    reschedule_event : Move an event to a different time
    """
    schedule = get_active_schedule()
    
    # Find the event
    matching_events = [e for e in schedule.events if e.title == event_title]
    if not matching_events:
        raise ValueError(f"Event '{event_title}' not found")
    
    event = matching_events[0]
    
    # Update status
    status_map = {
        "scheduled": EventStatus.SCHEDULED,
        "in_progress": EventStatus.IN_PROGRESS,
        "completed": EventStatus.COMPLETED,
        "cancelled": EventStatus.CANCELLED,
        "rescheduled": EventStatus.RESCHEDULED
    }
    
    event.status = status_map[new_status.lower()]
    
    return event.to_dict()


@mcp.tool()
def update_event_priority(
    event_title: str,
    new_priority: str
) -> Dict[str, Any]:
    """
    Update the priority of an event.
    
    Changes the priority level of an event. Searches for the event
    by title in the active schedule.
    
    Parameters
    ----------
    event_title : str
        The title of the event to update
    new_priority : str
        The new priority: "LOW", "MEDIUM", "HIGH", or "URGENT"
    
    Returns
    -------
    dict
        Updated event dictionary
    
    Raises
    ------
    ValueError
        If event not found or priority is invalid
    
    Examples
    --------
    >>> update_event_priority("Team Meeting", "HIGH")
    # Increases meeting priority to HIGH
    
    >>> update_event_priority("Grocery Shopping", "LOW")
    # Lowers chore priority to LOW
    
    See Also
    --------
    get_events_by_priority : Filter events by priority
    update_event_status : Change event status
    """
    schedule = get_active_schedule()
    
    # Find the event
    matching_events = [e for e in schedule.events if e.title == event_title]
    if not matching_events:
        raise ValueError(f"Event '{event_title}' not found")
    
    event = matching_events[0]
    event.priority = EventPriority[new_priority]
    
    return event.to_dict()


@mcp.tool()
def add_tags_to_event(
    event_title: str,
    tags: List[str]
) -> Dict[str, Any]:
    """
    Add tags to an event.
    
    Tags provide flexible categorization for events. Multiple tags
    can be added for better organization and filtering.
    
    Parameters
    ----------
    event_title : str
        The title of the event
    tags : list of str
        List of tags to add
    
    Returns
    -------
    dict
        Updated event dictionary with new tags
    
    Raises
    ------
    ValueError
        If event not found
    
    Examples
    --------
    >>> add_tags_to_event("Team Meeting", ["important", "weekly"])
    # Tags meeting as important and weekly
    
    >>> add_tags_to_event("Gym Session", ["fitness", "morning-routine"])
    # Tags workout with custom categories
    
    Notes
    -----
    Duplicate tags are automatically prevented.
    Tags are case-sensitive.
    
    See Also
    --------
    remove_tags_from_event : Remove tags from an event
    get_events_by_tag : Find events by tag
    """
    schedule = get_active_schedule()
    
    # Find the event
    matching_events = [e for e in schedule.events if e.title == event_title]
    if not matching_events:
        raise ValueError(f"Event '{event_title}' not found")
    
    event = matching_events[0]
    for tag in tags:
        event.add_tag(tag)
    
    return event.to_dict()


@mcp.tool()
def remove_tags_from_event(
    event_title: str,
    tags: List[str]
) -> Dict[str, Any]:
    """
    Remove tags from an event.
    
    Removes specified tags from an event's tag list.
    
    Parameters
    ----------
    event_title : str
        The title of the event
    tags : list of str
        List of tags to remove
    
    Returns
    -------
    dict
        Updated event dictionary
    
    Raises
    ------
    ValueError
        If event not found
    
    Examples
    --------
    >>> remove_tags_from_event("Team Meeting", ["weekly"])
    # Removes the "weekly" tag
    
    See Also
    --------
    add_tags_to_event : Add tags to an event
    get_events_by_tag : Find events by tag
    """
    schedule = get_active_schedule()
    
    # Find the event
    matching_events = [e for e in schedule.events if e.title == event_title]
    if not matching_events:
        raise ValueError(f"Event '{event_title}' not found")
    
    event = matching_events[0]
    for tag in tags:
        event.remove_tag(tag)
    
    return event.to_dict()


@mcp.tool()
def delete_event(event_title: str) -> str:
    """
    Delete an event from the schedule.
    
    Permanently removes an event by its title from the active schedule.
    
    Parameters
    ----------
    event_title : str
        The title of the event to delete
    
    Returns
    -------
    str
        Confirmation message
    
    Raises
    ------
    ValueError
        If event not found
    
    Examples
    --------
    >>> delete_event("Old Meeting")
    'Deleted event: Old Meeting'
    
    Notes
    -----
    This operation cannot be undone.
    If multiple events have the same title, only the first is deleted.
    
    See Also
    --------
    update_event_status : Mark event as cancelled instead of deleting
    clear_schedule : Delete all events
    """
    schedule = get_active_schedule()
    
    # Find the event
    matching_events = [e for e in schedule.events if e.title == event_title]
    if not matching_events:
        raise ValueError(f"Event '{event_title}' not found")
    
    event = matching_events[0]
    schedule.remove_event(event)
    
    return f"Deleted event: {event_title}"


# ============================================================================
# Resources - provide read-only access to schedule data
# ============================================================================

@mcp.resource("schedule://active/summary")
def get_active_schedule_summary() -> str:
    """
    Get a text summary of the active schedule.
    
    Returns
    -------
    str
        A formatted text summary with schedule name and key statistics
    """
    schedule = get_active_schedule()
    stats = schedule.get_statistics()
    
    summary = f"Schedule: {schedule.name}\n"
    summary += "=" * 50 + "\n\n"
    summary += f"Total Events: {stats['total_events']}\n"
    summary += f"Upcoming Events: {stats['upcoming_events']}\n"
    summary += f"Completed Events: {stats['completed_events']}\n"
    summary += f"Cancelled Events: {stats['cancelled_events']}\n\n"
    
    if stats['total_events'] > 0:
        summary += "Events by Type:\n"
        for event_type, count in stats['events_by_type'].items():
            summary += f"  - {event_type}: {count}\n"
        
        summary += f"\nTotal Scheduled Time: {stats['total_scheduled_minutes']} minutes\n"
        summary += f"Average Event Duration: {stats['average_event_duration']:.1f} minutes\n"
    
    return summary


@mcp.resource("schedule://active/upcoming")
def get_active_schedule_upcoming() -> str:
    """
    Get upcoming events as formatted text.
    
    Returns
    -------
    str
        Formatted list of upcoming events
    """
    schedule = get_active_schedule()
    events = schedule.get_upcoming_events(limit=20)
    
    if not events:
        return "No upcoming events scheduled."
    
    result = "Upcoming Events:\n"
    result += "=" * 50 + "\n\n"
    
    current_day = None
    for event in events:
        # Add day header if it's a new day
        if current_day is None or event.day != current_day:
            current_day = event.day
            result += f"\n{current_day}\n"
            result += "-" * 50 + "\n"
        
        result += f"  {event.time_range.to_12_hour_format()}: {event.title}\n"
        result += f"    Type: {event.get_event_type()}\n"
        result += f"    Priority: {event.priority.name}\n"
        if event.description:
            result += f"    Description: {event.description}\n"
        result += "\n"
    
    return result


# ============================================================================
# Prompts - provide common scheduling workflows
# ============================================================================

@mcp.prompt()
def schedule_meeting_prompt(
    title: str,
    date: str,
    duration_minutes: int
) -> str:
    """
    Generate a prompt for scheduling a meeting.
    
    Parameters
    ----------
    title : str
        Meeting title
    date : str
        Preferred date (YYYY-MM-DD)
    duration_minutes : int
        Expected duration in minutes
    
    Returns
    -------
    str
        A prompt to help schedule the meeting
    """
    return f"""Please help me schedule a meeting with the following details:
    
Title: {title}
Preferred Date: {date}
Duration: {duration_minutes} minutes

Steps to take:
1. Check for conflicts on {date} using check_conflicts
2. If conflicts exist, find free time slots using get_free_time_slots
3. Create the meeting using create_work_meeting or create_appointment
4. Confirm the scheduled time

Please suggest the best available time slot and create the meeting."""


@mcp.prompt()
def daily_schedule_review_prompt(date: str) -> str:
    """
    Generate a prompt for reviewing a day's schedule.
    
    Parameters
    ----------
    date : str
        Date to review (YYYY-MM-DD)
    
    Returns
    -------
    str
        A prompt for daily schedule review
    """
    return f"""Please provide a comprehensive review of my schedule for {date}:

1. List all events scheduled for that day
2. Identify any high-priority or urgent items
3. Check for scheduling conflicts
4. Show any free time slots available
5. Provide recommendations for the day

Please format the review in a clear, organized manner."""


@mcp.prompt()
def weekly_planning_prompt(start_date: str) -> str:
    """
    Generate a prompt for weekly planning.
    
    Parameters
    ----------
    start_date : str
        Monday of the week to plan (YYYY-MM-DD)
    
    Returns
    -------
    str
        A prompt for weekly planning
    """
    return f"""Please help me plan my week starting {start_date}:

1. Show all events scheduled for the week
2. Identify the busiest days
3. Highlight high-priority and urgent items
4. Suggest good times for additional activities
5. Check for any scheduling issues

Please provide a clear weekly overview with recommendations."""


# ============================================================================
# Main entry point
# ============================================================================

if __name__ == "__main__":
    # Run the FastMCP server
    mcp.run()
